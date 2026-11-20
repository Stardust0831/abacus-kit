import tempfile
import unittest
from math import prod
from pathlib import Path
from unittest.mock import patch

from abacus_kit.project import Project
from abacus_kit.rules import SCHEMA, Settings, manual, resolve


class BuilderTest(unittest.TestCase):
    def test_task_rebuilds_children_and_retains_geometry(self):
        p = Project()
        p.set_repeat("2x2x2")
        p.change("ecutwfc", "75")
        p.change("calculation", "md")
        self.assertEqual(p.settings.values["ecutwfc"], 50)
        self.assertEqual(len(p.structure) * prod(p.repeat), 16)
        p.change("md_type", "npt")
        p.change("md_pfirst", "2")
        self.assertEqual(p.settings.values["md_plast"], 2)
        p.change("md_type", "nve")
        self.assertNotIn("md_plast", p.settings.values)
        p.change("calculation", "scf")
        self.assertFalse(any(k.startswith("md_") for k in p.settings.values))

    def test_solver_controls_assets_and_output(self):
        p = Project()
        p.change("basis_type", "lcao")
        self.assertIn("NUMERICAL_ORBITAL", p.files()[0]["STRU"])
        p.change("esolver_type", "dp")
        files, assets, _ = p.files()
        self.assertEqual(list(assets), ["assets/model.pb"])
        self.assertNotIn("KPT", files)
        self.assertNotIn("ecutwfc", files["INPUT"])
        self.assertNotIn("NUMERICAL_ORBITAL", files["STRU"])
        p.change("esolver_type", "ksdft")
        self.assertNotIn("dp_fparam", p.visible_keys())

    def test_cutoff_order_and_rejected_edit(self):
        state = Settings()
        state.change("ecutrho", "240")
        self.assertEqual(state.values["ecutwfc"], 60)
        state.change("ecutwfc", "50")
        with self.assertRaisesRegex(ValueError, "ecutrho"):
            state.change("ecutrho", "120")
        self.assertEqual(state.values["ecutrho"], 240)
        reversed_schema = dict(reversed(list(SCHEMA.items())))
        with patch("abacus_kit.rules.SCHEMA", reversed_schema):
            self.assertEqual(resolve(state.requests)[0], state.values)
            self.assertEqual(resolve({})[0]["ecutrho"], 200)

    def test_spin_and_derived_defaults(self):
        state = Settings()
        for key, value in [("nspin", "2"), ("sc_mag_switch", "true"), ("sc_scf_thr", "10")]:
            state.change(key, value)
        self.assertAlmostEqual(state.values["mixing_restart"], 1e-10, places=18)
        state.change("mixing_restart", "0")
        state.change("sc_scf_thr", "0.001")
        self.assertEqual(state.values["mixing_restart"], 0)
        state.change("mixing_restart")
        self.assertEqual(state.values["mixing_restart"], 0.001)

    def test_thermostat_and_requirements(self):
        state = Settings()
        state.change("calculation", "md")
        state.change("md_dt", "2")
        self.assertEqual(state.values["md_tfreq"], 0.0125)
        state.change("md_thermostat", "csvr")
        self.assertEqual(state.values["md_csvr_tau"], 200)
        self.assertNotIn("md_tfreq", state.values)
        with self.assertRaises(ValueError):
            state.change("cal_force", "false")
        with self.assertRaises(ValueError):
            state.change("md_dt", "nan")
        state.change("cal_stress", "false")
        state.change("md_type", "npt")
        self.assertTrue(state.values["cal_stress"])

    def test_model_dimensions_and_species(self):
        p = Project("python")
        p.change("esolver_type", "dp")
        self.assertNotIn("dp_fparam", p.visible_keys())
        with patch.object(p, "model_info", return_value=(["Al"], 1, 2)):
            problems = p.files()[2]
            self.assertTrue(any("Si" in m for m in problems))
            self.assertTrue(any("dp_fparam" in m for m in problems))
            self.assertTrue(any("dp_aparam" in m for m in problems))
            p.set_crystal("Al", "fcc", 4.05)
            p.change("dp_fparam", "0")
            p.set_repeat("2 1 1")
            p.change("dp_aparam", "0 1 2 3")
            self.assertEqual(p.files()[2], ["assets/model.pb requires a nonempty file"])
        with patch.object(p, "model_info", return_value=(["Al"], 0, 0)):
            # External replacement at the same path leaves the old request accessible.
            self.assertIn("dp_aparam", p.visible_keys())
            self.assertTrue(any("dp_aparam requires 0" in m for m in p.files()[2]))
            p.change("dp_aparam")
            self.assertNotIn("dp_aparam", p.visible_keys())
            # Choosing a new file explicitly rebuilds all of its channels.
            changes = p.change("pot_file", "another.pb")
            self.assertIn(("dp_fparam", [0.0], []), changes)
            self.assertNotIn("dp_fparam", p.visible_keys())
            with self.assertRaisesRegex(ValueError, "unavailable"):
                p.change("dp_fparam", "2")

    def test_model_metadata_required_for_export(self):
        project = Project()
        project.change("esolver_type", "dp")
        with tempfile.TemporaryDirectory() as tmp:
            model = Path(tmp) / "potential.pb"
            model.write_bytes(b"fixture")
            project.change("pot_file", model)
            dest = Path(tmp) / "case"
            with self.assertRaisesRegex(ValueError, "Model metadata"):
                project.export(dest)
            self.assertFalse(dest.exists())

    def test_export_matches_preview_and_preserves_existing_files(self):
        p = Project()
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            dest = folder / "case"
            with self.assertRaisesRegex(ValueError, "nonempty"):
                p.export(dest)
            pp = folder / "Si.upf"
            pp.write_text("test pseudopotential\n")
            p.set_asset("pseudo", "Si", pp)
            preview = p.files()[0]
            with self.assertRaisesRegex(ValueError, "not found"):
                p.export(dest, folder / "absent-abacus")
            self.assertFalse(dest.exists())
            p.export(dest)
            for name, content in preview.items():
                self.assertEqual((dest / name).read_text(), content)
            with self.assertRaisesRegex(ValueError, "new calculation directory"):
                p.export(dest)

    def test_manual_covers_registry(self):
        report = manual()
        for key in SCHEMA:
            self.assertIn(f"| `{key}` |", report)
        self.assertIn("scf_thr / 10.0", report)
        self.assertIn("dim_aparam > 0", report)

    def test_reader_overwrite_prevents_export(self):
        p = Project()
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            pp = folder / "Si.upf"
            pp.write_text("fixture\n")
            p.set_asset("pseudo", "Si", pp)
            reader = folder / "abacus"
            reader.write_text(
                "#!/bin/sh\n"
                "case \"$1\" in\n"
                "  --help) echo --check-input-values ;;\n"
                "  --check-input-values)\n"
                "    printf 'INPUT_VALUE\\tcalculation\\tmd\\n'\n"
                "    echo 'INPUT parameters have been successfully checked!' ;;\n"
                "esac\n"
            )
            reader.chmod(0o755)
            dest = folder / "case"
            with self.assertRaisesRegex(ValueError, "calculation: requested scf, reported md"):
                p.export(dest, reader)
            self.assertFalse(dest.exists())


class TerminalTest(unittest.IsolatedAsyncioTestCase):
    async def test_edit_preview_error_and_export(self):
        from textual.widgets import DataTable, Input, Select, Static, TabbedContent
        from abacus_kit.ui import Builder, Editor
        project = Project()
        project.change("ecutwfc", "75")
        app = Builder(project)
        with tempfile.TemporaryDirectory() as tmp:
            pp = Path(tmp) / "Si.upf"
            pp.write_text("fixture\n")
            project.set_asset("pseudo", "Si", pp)
            async with app.run_test(size=(112, 34)) as pilot:
                await pilot.press("enter")
                app.screen.query_one(Select).value = "md"
                await pilot.click("#apply")
                self.assertEqual(project.settings.values["calculation"], "md")
                self.assertIn("md_type", app.row_keys)
                self.assertEqual(app.query_one(TabbedContent).active, "tab-Changes")
                changes = str(app.query_one("#view-Changes", Static).content)
                self.assertIn("ecutwfc: 75.0 [user] -> 50.0 [preset]", changes)
                table = app.query_one(DataTable)
                table.move_cursor(row=app.row_keys.index("md_dt"))
                app.action_edit()
                await pilot.pause()
                app.screen.query_one(Input).value = "-2"
                await pilot.click("#apply")
                self.assertIsInstance(app.screen, Editor)
                self.assertEqual(project.settings.values["md_dt"], 1.0)
                app.screen.query_one(Input).value = "2"
                await pilot.press("enter")
                await pilot.pause()
                self.assertIn("md_dt 2.0", str(app.query_one("#view-INPUT", Static).content))
                await pilot.press("x")
                app.screen.query_one(Input).value = str(Path(tmp) / "exported")
                await pilot.click("#apply")
                self.assertTrue((Path(tmp) / "exported/STRU").is_file())
