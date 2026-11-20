"""Full-screen terminal frontend. All decisions are made by the project model."""
from math import prod

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Checkbox, DataTable, Footer, Header, Input, Label, Select, Static, TabbedContent, TabPane

from . import catalog
from .project import CLASSICAL, LATTICES, triple
from .rules import SCHEMA, text_value


class Editor(ModalScreen):
    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, title, fields, apply, automatic=False):
        super().__init__()
        self.heading = title
        self.fields = fields
        self.apply_edit = apply
        self.automatic = automatic

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(self.heading, id="heading")
            for key, initial, options in self.fields:
                yield Label(key)
                if options:
                    choices = [(str(x), str(x)) for x in options]
                    yield Select(choices, value=str(initial), allow_blank=False, id="edit-" + key)
                else:
                    yield Input(str(initial), id="edit-" + key)
            yield Static("", id="problem", markup=False)
            with Horizontal(classes="buttons"):
                yield Button("Apply", id="apply", variant="primary")
                if self.automatic:
                    yield Button("Use default", id="auto")
                yield Button("Cancel", id="cancel")

    def on_mount(self):
        self.query_one("#edit-" + self.fields[0][0]).focus()

    def action_cancel(self):
        self.dismiss()

    def submit(self, automatic=False):
        data = {key: self.query_one("#edit-" + key).value for key, _, _ in self.fields}
        try:
            self.apply_edit(None if automatic else data)
        except (ValueError, OSError, KeyError, RuntimeError, OverflowError) as error:
            self.query_one("#problem", Static).update(str(error))
            self.query_one("#edit-" + self.fields[0][0]).focus()
            return
        self.dismiss()

    def on_input_submitted(self):
        self.submit()

    def on_button_pressed(self, event):
        if event.button.id == "cancel":
            self.dismiss()
        else:
            self.submit(event.button.id == "auto")


class Catalogue(ModalScreen):
    BINDINGS = [("escape", "close", "Close")]
    CSS = """
    Catalogue { align: center middle; }
    #catalogue { width: 96%; height: 95%; border: solid $primary; background: $surface; padding: 0 1; }
    #search { width: 1fr; }
    #category { width: 45%; }
    #filters, #actions { height: 3; }
    #results { width: 50%; }
    #definition { padding: 0 1; }
    #detail-pane { width: 50%; border-left: solid $primary; }
    #hits { width: 1fr; }
    """

    def __init__(self, project):
        super().__init__()
        self.project = project
        self.context = project.context()
        self.keys = []

    def compose(self):
        categories = sorted({field["category"] for field in catalog.PARAMETERS.values()})
        with Vertical(id="catalogue"):
            with Horizontal(id="filters"):
                yield Input(placeholder="Search keywords and descriptions", id="search")
                yield Select([("All categories", "")] + [(c, c) for c in categories],
                             allow_blank=False, value="", id="category")
            yield Checkbox("Include inactive keywords", id="include-inactive")
            with Horizontal():
                yield DataTable(id="results", cursor_type="row")
                with VerticalScroll(id="detail-pane"):
                    yield Static("", id="definition", markup=False)
            with Horizontal(id="actions"):
                yield Static("", id="hits")
                yield Button("Edit", id="catalog-edit", variant="primary")
                yield Button("Close", id="catalog-close")

    def on_mount(self):
        self.query_one(DataTable).add_columns("Keyword", "Status")
        self.filter_rows()
        self.query_one("#search").focus()

    def filter_rows(self):
        table = self.query_one(DataTable)
        table.clear()
        self.keys = []
        query = self.query_one("#search", Input).value
        category = self.query_one("#category", Select).value
        include = self.query_one(Checkbox).value
        for key in catalog.search(query, category):
            available = self.project.availability(key, self.context)
            if available is False and not include:
                continue
            status = "inactive" if available is False else "reader-dependent" if available is None else "available"
            if key in self.project.values:
                status = self.project.settings.origins.get(key) or "user"
            self.keys.append(key)
            table.add_row(key, status)
        self.query_one("#hits", Static).update(f"{len(self.keys)} of {len(catalog.PARAMETERS)} keywords")
        self.show_details()

    def show_details(self):
        row = self.query_one(DataTable).cursor_row
        key = self.keys[row] if 0 <= row < len(self.keys) else None
        text = catalog.details(key) if key else ""
        if key:
            value = self.project.values.get(key)
            text += "\n\nCurrent INPUT: " + ("omitted" if value is None else text_value(value))
            if key in SCHEMA and SCHEMA[key].get("when"):
                text += "\nEditor condition: " + SCHEMA[key]["when"]
            if key in SCHEMA and SCHEMA[key].get("model_dimension"):
                text += "\nRequired model dimension: " + SCHEMA[key]["model_dimension"] + " > 0"
        self.query_one("#definition", Static).update(text)
        self.query_one("#detail-pane", VerticalScroll).scroll_home(animate=False)
        self.query_one("#catalog-edit", Button).disabled = not key or self.project.availability(key, self.context) is False

    def on_input_changed(self):
        self.filter_rows()

    def on_select_changed(self):
        self.filter_rows()

    def on_checkbox_changed(self):
        self.filter_rows()

    def on_input_submitted(self):
        self.query_one(DataTable).focus()

    def on_data_table_row_highlighted(self):
        self.show_details()

    def on_data_table_row_selected(self, event):
        event.stop()
        self.pick()

    def pick(self):
        if not self.query_one("#catalog-edit", Button).disabled:
            self.dismiss(self.keys[self.query_one(DataTable).cursor_row])

    def action_close(self):
        self.dismiss()

    def on_button_pressed(self, event):
        event.stop()
        if event.button.id == "catalog-edit":
            self.pick()
        else:
            self.dismiss()


class Builder(App):
    TITLE = "ABACUS Input"
    CSS = """
    Screen { background: $surface; }
    #tools { height: 3; }
    #tools Button, .buttons Button { min-width: 9; margin-right: 1; }
    #body { height: 1fr; }
    #parameters { width: 54%; }
    #preview { width: 46%; border-left: solid $primary; }
    #summary, #status { height: auto; max-height: 3; padding: 0 1; }
    #summary { text-style: bold; color: $accent; }
    #status { color: $warning; }
    .doc { padding: 0 1; }
    Editor { align: center middle; background: $background 80%; }
    #dialog { width: 62; max-width: 98%; height: auto; max-height: 100%; overflow-y: auto;
              background: $panel; border: solid $primary; padding: 0 2 1 2; }
    #heading { text-style: bold; margin: 1 0; }
    #problem { color: $error; height: auto; max-height: 6; }
    .buttons { height: 3; margin-top: 1; }
    """
    BINDINGS = [("e", "edit", "Edit"), ("p", "catalogue", "Parameters"), ("c", "crystal", "Crystal"),
                ("x", "export", "Export"), ("q", "quit", "Quit")]

    def __init__(self, project, abacus=None):
        super().__init__()
        self.project = project
        self.abacus = abacus
        self.history = []
        self.row_keys = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="tools"):
            for key, title in (("catalog", "Parameters"), ("crystal", "Crystal"), ("import", "Import"), ("repeat", "Supercell"),
                               ("mesh", "K mesh"), ("export", "Export")):
                yield Button(title, id=key)
        yield Static("", id="summary", markup=False)
        with Horizontal(id="body"):
            yield DataTable(id="parameters", cursor_type="row")
            with TabbedContent(id="preview"):
                for name in ("INPUT", "STRU", "KPT", "Changes"):
                    with TabPane(name, id="tab-" + name):
                        with VerticalScroll():
                            yield Static("", id="view-" + name, classes="doc", markup=False)
        yield Static("", id="status", markup=False)
        yield Footer()

    def on_mount(self):
        self.query_one(DataTable).add_columns("Parameter", "Value", "Source")
        self.draw()
        self.query_one(DataTable).focus()

    def draw(self, message=""):
        project = self.project
        settings = project.settings
        files, assets, missing = project.files()
        table = self.query_one(DataTable)
        index = table.cursor_row
        table.clear()
        self.row_keys = project.visible_keys()
        for key in self.row_keys:
            value = project.values[key]
            depth = 0
            ancestor = key
            while ancestor := SCHEMA.get(ancestor, {}).get("parent"):
                depth += 1
            table.add_row("  " * depth + key, text_value(value) if value != [] else "(empty)", settings.origins.get(key) or "user")
        if settings.values["esolver_type"] not in CLASSICAL:
            for kind, paths in (("pseudo", project.pseudos), ("orbital", project.orbitals)):
                if kind == "orbital" and settings.values["basis_type"] not in ("lcao", "lcao_in_pw"):
                    continue
                for symbol in project.species:
                    self.row_keys.append((kind, symbol))
                    table.add_row(f"{symbol} {kind}", str(paths.get(symbol, "(select file)")), "STRU")
        table.move_cursor(row=min(index, len(self.row_keys) - 1))
        self.query_one("#mesh", Button).disabled = "KPT" not in files
        self.query_one("#export", Button).disabled = bool(missing)
        formula = project.structure.get_chemical_formula()
        count = len(project.structure) * prod(project.repeat)
        self.query_one("#summary", Static).update(
            f"{settings.values['calculation'].upper()}  |  {formula}  |  {count} atoms  |  "
            + " x ".join(map(str, project.repeat)))
        for name in ("INPUT", "STRU", "KPT"):
            self.query_one("#view-" + name, Static).update(files.get(name, "K points are unused for this solver."))
        self.query_one("#view-Changes", Static).update("\n".join(self.history))
        status = "  |  ".join(missing) or message
        if not status and settings.values["esolver_type"] == "dp" and not project.deepmd_python:
            status = "DeePMD model dimensions unverified"
        self.query_one("#status", Static).update(status)

    def edit_key(self, key):
        project = self.project
        if isinstance(key, tuple):
            kind, symbol = key
            paths = project.pseudos if kind == "pseudo" else project.orbitals
            def attach(data):
                project.set_asset(kind, symbol, data["path"])
                self.draw(f"{symbol} {kind} -> {data['path']}")
            self.push_screen(Editor(f"{symbol} {kind}", [("path", paths.get(symbol, ""), None)], attach))
            return
        native = catalog.PARAMETERS[key]
        field = SCHEMA.get(key, {})
        current = project.values.get(key, "")
        choices = field.get("choices", native.get("allowed_values"))
        if field.get("type") == "bool" or native["kind"] == "bool":
            choices = ("0", "1")
        if choices and current == "":
            current = catalog.literal_defaults().get(key, choices[0])
        def apply(data):
            old_origins = project.settings.origins | dict.fromkeys(project.extra, "user")
            old_mesh = project.mesh
            changes = project.change(key, data["value"] if data is not None else None)

            def describe(value, origin):
                return "(inactive)" if origin is None else f"{text_value(value) or '(empty)'} [{origin}]"

            origins = project.settings.origins | dict.fromkeys(project.extra, "user")
            lines = [f"{name}: {describe(before, old_origins.get(name))} -> "
                     f"{describe(after, origins.get(name))}"
                     for name, before, after in changes]
            if old_mesh != project.mesh:
                lines.append(f"K mesh: {old_mesh} -> {project.mesh}")
            self.history[0:0] = lines + [""]
            self.draw(f"{key} applied. {len(lines)} updates." if lines else "")
            if any(name != key and old_origins.get(name) == "user" and origins.get(name) != "user"
                   for name, _, _ in changes):
                self.query_one(TabbedContent).active = "tab-Changes"
        unit = f" ({native['unit']})" if native.get("unit") else ""
        # Numeric enums may have word-like documentation defaults.
        if choices and str(text_value(current)) not in {str(choice) for choice in choices}:
            current = choices[0]
        self.push_screen(Editor(key + unit, [("value", text_value(current), choices)], apply, True))

    def action_edit(self):
        self.edit_key(self.row_keys[self.query_one(DataTable).cursor_row])

    def action_catalogue(self):
        self.push_screen(Catalogue(self.project), lambda key: self.edit_key(key) if key else None)

    def on_data_table_row_selected(self, event):
        self.edit_key(self.row_keys[event.cursor_row])

    def action_crystal(self):
        def create(data):
            self.project.set_crystal(data["formula"], data["lattice"], data["angstrom"])
            self.draw("Crystal updated")
        self.push_screen(Editor("Crystal", [("formula", "Si", None), ("lattice", "diamond", LATTICES),
                                            ("angstrom", "5.43", None)], create))

    def action_export(self):
        def save(data):
            path = self.project.export(data["directory"], self.abacus)
            self.draw(f"Exported {path} ({self.project.last_check})")
        self.push_screen(Editor("Export calculation", [("directory", "abacus-case", None)], save))

    def on_button_pressed(self, event):
        key = event.button.id
        if key == "catalog":
            self.action_catalogue()
        elif key == "crystal":
            self.action_crystal()
        elif key == "export":
            self.action_export()
        elif key == "import":
            def load(data):
                self.project.import_geometry(data["path"])
                self.draw("Structure imported")
            self.push_screen(Editor("Import structure", [("path", "", None)], load))
        elif key in ("mesh", "repeat"):
            current = self.project.mesh if key == "mesh" else self.project.repeat
            def resize(data):
                if key == "mesh":
                    self.project.mesh = triple(data["dimensions"])
                else:
                    self.project.set_repeat(data["dimensions"])
                self.draw()
            self.push_screen(Editor(event.button.label.plain, [("dimensions", " ".join(map(str, current)), None)], resize))
