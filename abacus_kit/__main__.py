import argparse
import importlib.util
import sys
from pathlib import Path

from .project import Project
from .rules import manual
from . import catalog


def main():
    parser = argparse.ArgumentParser(description="Interactive ABACUS input generator")
    parser.add_argument("--structure", type=Path, help="import a periodic ASE-readable structure")
    parser.add_argument("--abacus", help="check the staged calculation with this executable before export")
    parser.add_argument("--deepmd-python", help="Python with DeePMD for model type and dimension checks")
    parser.add_argument("--pseudo", metavar="ELEMENT=FILE", action="append", default=[])
    parser.add_argument("--orbital", metavar="ELEMENT=FILE", action="append", default=[])
    parser.add_argument("--manual", action="store_true", help="print editor rules and the complete registered catalogue")
    parser.add_argument("--list", nargs="?", const="", metavar="SEARCH", help="list registered keywords")
    parser.add_argument("--describe", metavar="KEY", help="show an upstream parameter definition")
    args = parser.parse_args()
    if args.list is not None:
        for key in catalog.search(args.list):
            print(f"{key}\t{catalog.PARAMETERS[key]['category']}")
        return
    if args.describe:
        key = args.describe.lower()
        if key not in catalog.PARAMETERS:
            parser.error(f"Unknown INPUT keyword: {key}")
        print(catalog.details(key))
        return
    if args.manual:
        print(manual(), end="")
        return
    try:
        from .ui import Builder
    except ModuleNotFoundError as error:
        if error.name != "textual":
            raise
        parser.exit(2, "Install the terminal editor with pip install abacus-kit.\n")
    deepmd_python = args.deepmd_python
    if not deepmd_python and importlib.util.find_spec("deepmd"):
        deepmd_python = sys.executable
    project = Project(deepmd_python)
    try:
        if args.structure:
            project.import_geometry(args.structure)
        for kind in ("pseudo", "orbital"):
            for assignment in getattr(args, kind):
                symbol, path = assignment.split("=", 1)
                project.set_asset(kind, symbol, path)
    except (OSError, ValueError, KeyError) as error:
        parser.error(str(error))
    Builder(project, args.abacus).run()


if __name__ == "__main__":
    main()
