import tempfile
import unittest
from pathlib import Path

from abacus_kit import catalog
from abacus_kit.project import Project
from abacus_kit.rules import SCHEMA, manual
from abacus_kit.verify import equivalent


class CatalogTest(unittest.TestCase):
    def test_registry_and_reference(self):
        entries = catalog.PARAMETERS
        self.assertEqual(len(entries), 637)
        self.assertEqual(sum(not v.get("documented", True) for v in entries.values()), 8)
        self.assertLessEqual(SCHEMA.keys(), entries.keys())
        reference = manual().split("## ABACUS input catalogue")[1]
        keys = [line.split("`")[1] for line in reference.splitlines() if line.startswith("| `")]
        self.assertCountEqual(keys, entries)
        for key, field in entries.items():
            for rule in ("availability", "value_rule"):
                if field.get(rule):
                    catalog.condition(field[rule])
        self.assertIn("cond_mgga_vel", catalog.search("meta-gga velocity"))

    def test_hierarchy_and_original_requests(self):
        p = Project()
        self.assertFalse(p.availability("efield_amp"))
        p.change("efield_flag", "true")
        p.change("efield_amp", "0.003")
        p.change("suffix", "Si")
        with self.assertRaises(ValueError):
            p.change("efield_amp", "NaN")
        self.assertIn("efield_amp 0.003\n", p.files()[0]["INPUT"])
        changes = p.change("efield_flag", "false")
        self.assertIn(("efield_amp", 0.003, None), changes)
        self.assertEqual(p.extra["suffix"], "Si")
        p.change("calculation", "md")
        self.assertEqual(p.extra, {})

    def test_paths_and_registered_only_keyword(self):
        p = Project()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pp = root / "Si.upf"
            pp.write_text("fixture\n")
            p.set_asset("pseudo", "Si", pp)
            p.change("stru_file", "geometry/Si.stru")
            p.change("kpoint_file", "sampling/KPOINTS")
            p.change("pseudo_dir", "PP")
            p.change("cond_mgga_vel", "off")
            p.change("kspacing", "0.1 0.2 0.3")
            p.change("ntype", "2")
            with self.assertRaisesRegex(ValueError, "ntype"):
                p.export(root / "bad")
            p.change("ntype", "1")
            with self.assertRaises(ValueError):
                p.change("stru_file", "../outside")
            dest = p.export(root / "case")
            for filename in ("geometry/Si.stru", "sampling/KPOINTS", "PP/assets/Si.upf"):
                self.assertTrue((dest / filename).is_file(), filename)
            self.assertIn("cond_mgga_vel 0\n", (dest / "INPUT").read_text())

    def test_tasks_vectors_and_constraints(self):
        p = Project()
        for task in catalog.PARAMETERS["calculation"]["allowed_values"]:
            p.change("calculation", task)
            self.assertEqual(p.values["calculation"], task)
            if task == "nscf":
                self.assertEqual(p.values["scf_nmax"], 1)
                with self.assertRaisesRegex(ValueError, "scf_nmax"):
                    p.change("scf_nmax", 2)
        p.change("calculation", "md")
        p.change("esolver_type", "lj")
        self.assertTrue(p.availability("lj_sigma"))
        self.assertNotIn("KPT", p.files()[0])
        p.change("lj_sigma", "3.4")
        p.change("esolver_type", "tddft")
        self.assertNotIn("lj_sigma", p.values)
        self.assertTrue(catalog.matches(catalog.condition("td_ttype contains 4"), {"td_ttype": [2, 4]}))
        self.assertIsNone(catalog.matches(catalog.condition("ks_solver==cg"), {}))
        self.assertTrue(equivalent("kspacing", "0.1", "0.1 0.1 0.1"))
        p.change("calculation", "scf")
        with self.assertRaisesRegex(ValueError, "unavailable"):
            p.change("mem_saver", "1")
        p.change("basis_type", "lcao")
        p.change("ks_solver", "cg")
        self.assertTrue(any("ks_solver" in msg for msg in p.files()[2]))
        with self.assertRaises(ValueError):
            p.change("cell_replica", "1 0 1")
        with self.assertRaises(ValueError):
            p.change("suffix", "Si\nntype 1")


class CatalogueScreenTest(unittest.IsolatedAsyncioTestCase):
    async def test_catalogue_search_edit_preview_and_inactive(self):
        from textual.widgets import Checkbox, DataTable, Input, Static
        from abacus_kit.ui import Builder, Catalogue, Editor
        p = Project()
        app = Builder(p)
        async with app.run_test(size=(115, 34)) as pilot:
            await pilot.press("p")
            await pilot.pause()
            browser = app.screen
            self.assertIsInstance(browser, Catalogue)
            browser.query_one("#search", Input).value = "efield_amp"
            await pilot.pause()
            self.assertNotIn("efield_amp", browser.keys)
            browser.query_one(Checkbox).value = True
            await pilot.pause()
            self.assertIn("efield_amp", browser.keys)
            browser.query_one("#search", Input).value = "nbands"
            await pilot.pause()
            results = browser.query_one(DataTable)
            results.move_cursor(row=browser.keys.index("nbands"))
            results.focus()
            await pilot.press("enter")
            await pilot.pause()
            self.assertIsInstance(app.screen, Editor)
            app.screen.query_one(Input).value = "12"
            await pilot.press("enter")
            await pilot.pause()
            self.assertIn("nbands", app.row_keys)
            self.assertIn("nbands 12", str(app.query_one("#view-INPUT", Static).content))
