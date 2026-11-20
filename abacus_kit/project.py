"""Crystal preparation, file previews and export of the confirmed configuration."""
import os
import shutil
import tempfile
from math import prod
from pathlib import Path, PurePosixPath

import numpy as np
from ase.build import bulk
from ase.constraints import FixAtoms, FixCartesian
from ase.io import read
from ase.io.formats import UnknownFileTypeError

from . import catalog
from .stru import write_stru
from .model import inspect_model
from .rules import SCHEMA, Settings, text_value
from .verify import check_reader


LATTICES = ("diamond", "fcc", "bcc", "sc", "rocksalt", "zincblende", "cesiumchloride")
CLASSICAL = {"dp", "nep", "snap", "lj"}


def relative_file(value):
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError(f"Choose a relative path inside the exported directory: {value}")
    return path.as_posix()


def triple(text):
    parts = str(text).lower().replace(",", " ").replace("x", " ").split()
    if len(parts) != 3 or any(not s.isdecimal() or int(s) < 1 for s in parts):
        raise ValueError("Enter three positive integers")
    return tuple(map(int, parts))


class Project:
    def __init__(self, deepmd_python=None):
        self.settings = Settings()
        self.extra = {}
        self.structure = bulk("Si", "diamond", a=5.43)
        self.mesh = (1, 1, 1)
        self.repeat = (1, 1, 1)
        self.pseudos = {}
        self.orbitals = {}
        self.deepmd_python = deepmd_python
        self.last_check = ""

    @property
    def values(self):
        return self.settings.values | self.extra

    def context(self):
        context = catalog.literal_defaults() | self.values
        if self.settings.values["esolver_type"] in CLASSICAL:
            context["basis_type"] = ""
        return context

    def availability(self, key, context=None):
        if key in SCHEMA:
            return key in self.visible_keys()
        return catalog.applicable(key, self.context() if context is None else context)

    def change(self, key, value=None):
        if key not in catalog.PARAMETERS:
            raise ValueError(f"Unknown INPUT keyword: {key}")
        if value is not None and self.availability(key) is False:
            raise ValueError(f"{key} is unavailable for this calculation and model")
        if key in SCHEMA:
            old = self.settings.values[key]
            if key == "pot_file" and value is not None and self.settings.values["esolver_type"] == "dp":
                self.model_info(value)
            changes = self.settings.change(key, value)
            if self.settings.values[key] != old and key in ("calculation", "esolver_type"):
                self.mesh = (1, 1, 1)
                if key == "calculation":
                    changes.extend((k, v, None) for k, v in self.extra.items())
                    self.extra.clear()
        else:
            old = self.extra.get(key)
            if value is None:
                self.extra.pop(key, None)
            else:
                parsed = catalog.parse(key, value)
                if key in ("stru_file", "kpoint_file"):
                    relative_file(parsed)
                elif key in ("pseudo_dir", "orbital_dir") and parsed not in (".", "./"):
                    relative_file(parsed)
                self.extra[key] = parsed
            changes = [(key, old, self.extra.get(key))] if old != self.extra.get(key) else []
        # A removed prerequisite can itself be the parent of another edited field.
        while True:
            context = self.context()
            inactive = [k for k in self.extra if self.availability(k, context) is False]
            if not inactive:
                break
            for name in inactive:
                changes.append((name, self.extra.pop(name), None))
        return changes

    def set_crystal(self, formula, lattice, constant):
        if lattice not in LATTICES:
            raise ValueError("Choose a lattice from " + ", ".join(LATTICES))
        a = float(constant)
        if not np.isfinite(a) or a <= 0:
            raise ValueError("Lattice constant must be positive (Angstrom)")
        self.set_geometry(bulk(formula, lattice, a=a))

    def import_geometry(self, path):
        try:
            atoms = read(Path(path).expanduser(), index=-1)
        except (UnknownFileTypeError, IndexError) as error:
            raise ValueError(f"Cannot read a structure from {path}: {error}") from error
        self.set_geometry(atoms)

    def set_geometry(self, atoms):
        if not len(atoms) or not all(atoms.pbc) or atoms.cell.rank != 3:
            raise ValueError("A three-dimensional periodic cell with atoms is required")
        if not np.all(np.isfinite(atoms.positions)) or not np.all(np.isfinite(atoms.cell)):
            raise ValueError("Nonfinite structure coordinates")
        if np.linalg.det(atoms.cell) <= 0:
            raise ValueError("A right-handed, nonsingular lattice is required")
        if any(not isinstance(c, (FixAtoms, FixCartesian)) for c in atoms.constraints):
            raise ValueError("This STRU writer supports FixAtoms and FixCartesian constraints")
        if atoms.has("momenta") and np.any(atoms.get_momenta()):
            raise ValueError("Import of per-atom velocities is not supported by the STRU writer")
        if atoms.has("masses") or np.any(atoms.get_initial_charges()):
            raise ValueError("Custom atomic masses and per-atom charge assignments require a native STRU")
        self.structure = atoms
        self.repeat = (1, 1, 1)

    @property
    def species(self):
        return list(dict.fromkeys(self.structure.get_chemical_symbols()))

    def set_repeat(self, raw):
        self.repeat = triple(raw)

    def model_info(self, filename):
        path = Path(filename).expanduser().resolve()
        if self.deepmd_python and path.is_file():
            stat = path.stat()
            return inspect_model(self.deepmd_python, path, stat.st_mtime_ns, stat.st_size)
        return None

    def visible_keys(self):
        values = self.settings.values
        if values["esolver_type"] != "dp":
            return list(values) + list(self.extra)
        try:
            info = self.model_info(values["pot_file"])
        except (OSError, ValueError):
            info = None
        dims = {"dim_fparam": info[1], "dim_aparam": info[2]} if info else {}
        # Keep stale explicit values editable if the model was replaced on disk.
        return [key for key in values if "model_dimension" not in SCHEMA[key]
                or dims.get(SCHEMA[key]["model_dimension"], 0) > 0 or values[key]] + list(self.extra)

    def set_asset(self, kind, element, filename):
        if element not in self.species:
            raise ValueError(f"{element} is absent from the structure")
        path = Path(filename).expanduser().resolve()
        if not path.is_file():
            raise ValueError(f"File does not exist: {path}")
        collection = self.pseudos if kind == "pseudo" else self.orbitals
        collection[element] = path

    def files(self):
        values = self.values
        electronic = values["esolver_type"] not in CLASSICAL
        assets, missing = {}, []
        data = {key: text_value(v) for key, v in values.items() if v != []}
        pseudos = {}
        orbitals = {} if values.get("basis_type") in ("lcao", "lcao_in_pw") else None
        if electronic:
            for symbol in self.species:
                pseudos[symbol] = f"assets/{symbol}.upf"
                assets[str(PurePosixPath(values.get("pseudo_dir", ".")) / pseudos[symbol])] = self.pseudos.get(symbol)
                if orbitals is not None:
                    orbitals[symbol] = f"assets/{symbol}.orb"
                    assets[str(PurePosixPath(values.get("orbital_dir", ".")) / orbitals[symbol])] = self.orbitals.get(symbol)
        elif "pot_file" in values:
            model = Path(values["pot_file"]).expanduser().resolve()
            try:
                info = self.model_info(model) if values["esolver_type"] == "dp" else None
            except (OSError, ValueError) as error:
                info = None
                missing.append(str(error))
            if values["esolver_type"] == "dp" and model.is_file() and not self.deepmd_python:
                missing.append("Model metadata required: select a DeePMD interpreter with --deepmd-python")
            if info:
                species, frames, atomic = info
                unsupported = set(self.species) - set(species)
                if species and unsupported:
                    missing.append("Model does not contain " + ", ".join(sorted(unsupported)))
                if len(values["dp_fparam"]) != frames:
                    missing.append(f"dp_fparam requires {frames} frame values")
                count = len(self.structure) * prod(self.repeat)
                if len(values["dp_aparam"]) not in (atomic, count * atomic):
                    missing.append(f"dp_aparam requires {atomic} or {count * atomic} values in STRU order")
            extension = model.suffix
            if any(not (c.isalnum() or c == ".") for c in extension):
                raise ValueError("The potential filename has an unsupported extension")
            data["pot_file"] = f"assets/model{extension}"
            assets[data["pot_file"]] = model
            if values["esolver_type"] == "snap":
                coefficient = Path(values.get("snap_param_file", "snap.param")).expanduser().resolve()
                data["snap_param_file"] = "assets/snap.param"
                assets["assets/snap.param"] = coefficient
        context = self.context()
        for owner, when, required in catalog.REQUIREMENTS:
            if when and catalog.matches(when, context) is not True:
                continue
            if catalog.matches(catalog.condition(required), context) is False:
                missing.append(f"{owner} requires {required}")
        if "ntype" in values and values["ntype"] not in (0, len(self.species)):
            missing.append(f"ntype must match the {len(self.species)} species in STRU")
        for key in ("orbital_corr", "hubbard_u"):
            if key in values and len(text_value(values[key]).split()) != len(self.species):
                missing.append(f"{key} needs one entry per species in STRU")
        for target, source in assets.items():
            if source is None or not source.is_file() or source.stat().st_size == 0:
                missing.append(f"{target} requires a nonempty file")
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            write_stru(self.structure.repeat(self.repeat), tmp, pseudos, orbitals)
            content = {"INPUT": "INPUT_PARAMETERS\n" + "".join(f"{k} {v}\n" for k, v in data.items()) + "\n",
                       "STRU": (directory / "STRU").read_text()}
        if electronic:
            content["KPT"] = "K_POINTS\n0\nGamma\n" + " ".join(map(str, self.mesh)) + " 0 0 0\n"
        paths = [PurePosixPath(self.filename(name)) for name in content] + list(map(PurePosixPath, assets))
        if len(set(paths)) != len(paths) or any(p in q.parents for p in paths for q in paths):
            missing.append("INPUT, STRU, KPT and their assets require distinct paths")
        return content, assets, missing

    def filename(self, name):
        variable = {"STRU": "stru_file", "KPT": "kpoint_file"}.get(name)
        return self.extra.get(variable, name)

    def export(self, destination, abacus=None):
        content, assets, missing = self.files()
        if missing:
            raise ValueError("\n".join(missing))
        dest = Path(destination).expanduser().absolute()
        if dest.exists():
            raise ValueError(f"Choose a new calculation directory: {dest}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=dest.parent) as tmp:
            stage = Path(tmp) / "calculation"
            stage.mkdir()
            for name, text in content.items():
                path = stage / self.filename(name)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text)
            for name, source in assets.items():
                target = stage / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
            if abacus:
                executable = shutil.which(os.fspath(abacus))
                if not executable:
                    raise ValueError(f"ABACUS executable not found: {abacus}")
                executable = str(Path(executable).resolve())
                # Some readers create output files. Check an identical disposable case.
                check = Path(tmp) / "check"
                shutil.copytree(stage, check)
                requested = dict(line.split(maxsplit=1) for line in
                                 content["INPUT"].splitlines()[1:] if line.strip())
                checked = check_reader(executable, check, requested)
            stage.rename(dest)
            self.last_check = checked if abacus else "generator checks passed"
        return dest
