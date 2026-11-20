"""Evaluate the generator's parameter registry against the current requests."""
import ast
import json
import math
import operator
from functools import lru_cache
from pathlib import Path

from .catalog import PARAMETERS, REGISTRY


SCHEMA = json.loads(Path(__file__).with_name("schema.json").read_text())
for _name, _field in SCHEMA.items():
    if _field["type"] == "choice" and "choices" not in _field:
        _field["choices"] = PARAMETERS[_name]["allowed_values"]
BINARY = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
          ast.Div: operator.truediv, ast.Eq: operator.eq, ast.NotEq: operator.ne,
          ast.GtE: operator.ge, ast.LtE: operator.le, ast.In: lambda item, items: item in items,
          ast.NotIn: lambda item, items: item not in items}


@lru_cache
def expression(source):
    return ast.parse(source, mode="eval").body


def evaluate(node, lookup, supplied):
    def value(child):
        return evaluate(child, lookup, supplied)

    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        return lookup(node.id)
    if isinstance(node, ast.Tuple):
        return tuple(map(value, node.elts))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return not value(node.operand)
    if isinstance(node, ast.BoolOp):
        test = all if isinstance(node.op, ast.And) else any
        return test(value(child) for child in node.values)
    if isinstance(node, ast.Compare) and len(node.ops) == 1:
        return BINARY[type(node.ops[0])](value(node.left), value(node.comparators[0]))
    if isinstance(node, ast.BinOp):
        return BINARY[type(node.op)](value(node.left), value(node.right))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "given":
        return value(node.args[0]) in supplied
    raise ValueError(f"Unsupported rule: {ast.unparse(node)}")


def parse_value(key, raw):
    field = SCHEMA[key]
    kind = field["type"]
    if kind == "choice":
        for choice in field["choices"]:
            if str(choice) == str(raw):
                return choice
        raise ValueError(f"{key} accepts {', '.join(map(str, field['choices']))}")
    if kind == "bool":
        choices = {"true": True, "false": False, "1": True, "0": False}
        if str(raw).lower() not in choices:
            raise ValueError(f"{key} accepts true or false")
        return choices[str(raw).lower()]
    if kind == "file":
        if not str(raw).strip():
            raise ValueError(f"{key} requires a filename")
        return str(raw)
    if kind == "vector":
        values = [float(item) for item in str(raw).replace(",", " ").split()]
        if not all(map(math.isfinite, values)):
            raise ValueError(f"{key} requires finite numbers")
        return values
    number = int(str(raw)) if kind == "integer" else float(raw)
    if not math.isfinite(number) or (field.get("positive") and number <= 0):
        raise ValueError(f"{key} requires a finite {'positive ' if field.get('positive') else ''}value")
    if "min" in field and number < field["min"]:
        raise ValueError(f"{key} must be at least {field['min']}")
    return number


def text_value(value):
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, list):
        return " ".join(map(str, value))
    return str(value)


def resolve(requests):
    values, origins = {}, {}
    stack = []

    def get(key):
        if key in values:
            return values[key]
        if key in stack:
            raise ValueError("Default dependency cycle: " + " -> ".join(stack + [key]))
        stack.append(key)
        field = SCHEMA[key]

        def run(source):
            return evaluate(expression(source), get, requests)

        if "when" in field and not run(field["when"]):
            result, origin = None, None
        elif key in requests:
            result, origin = requests[key], "user"
        elif "default" in field:
            result, origin = field["default"], "preset"
        else:
            for case in field["cases"]:
                if "when" not in case or run(case["when"]):
                    result = run(case["expr"]) if "expr" in case else case["value"]
                    origin = case.get("expr", case.get("when", "preset"))
                    break
            else:
                raise ValueError(f"No default matches {key}")
        if isinstance(result, float) and not math.isfinite(result):
            raise ValueError(f"The default for {key} is outside the finite range")
        if result is not None and field.get("positive") and result <= 0:
            raise ValueError(f"{key} requires a positive value")
        stack.pop()
        values[key], origins[key] = result, origin
        return result

    for key in SCHEMA:
        get(key)
    return {k: values[k] for k in SCHEMA if values[k] is not None}, origins


def descendants(key):
    def parents(name):
        while parent := SCHEMA[name].get("parent"):
            yield parent
            name = parent
    return {name for name in SCHEMA if key in parents(name)}


class Settings:
    def __init__(self):
        self.requests = {}
        self.values, self.origins = resolve({})

    def change(self, key, raw=None):
        if key not in self.values:
            raise ValueError(f"{key} is unavailable in this calculation")
        requested = self.requests.copy()
        if raw is None:
            requested.pop(key, None)
        else:
            requested[key] = parse_value(key, raw)
        values, origins = resolve(requested)
        if values[key] != self.values[key]:
            for child in descendants(key):
                requested.pop(child, None)
            values, origins = resolve(requested)
        for name in tuple(requested):
            if name not in values:
                del requested[name]
        values, origins = resolve(requested)
        for name, field in SCHEMA.items():
            if name in values and "requires" in field:
                if not evaluate(expression(field["requires"]), values.get, requested):
                    if key not in field.get("restore_on_conflict", ()):
                        raise ValueError(field.get("error", f"{name} conflicts with {field['requires']}"))
                    requested.pop(name, None)
                    values, origins = resolve(requested)
        changes = []
        for name in SCHEMA:
            before, after = self.values.get(name), values.get(name)
            if before != after or self.origins.get(name) != origins.get(name):
                changes.append((name, before, after))
        self.requests, self.values, self.origins = requested, values, origins
        return changes


def manual():
    rows = ["# Input generator parameter rules", "",
            "A task change rebuilds its descendants. Formula defaults follow their dependencies until edited.",
            "", "| Parameter | Parent | Visible when | Default in the generator | Constraints |",
            "| --- | --- | --- | --- | --- |"]
    for key, field in SCHEMA.items():
        if "cases" in field:
            parts = []
            for case in field["cases"]:
                value = case.get("expr", case.get("value"))
                parts.append(f"{case.get('when', 'otherwise')}: {value}")
            default = " / ".join(parts)
        else:
            default = str(field["default"])
        visible = field.get("when", "always")
        if "model_dimension" in field:
            visible += f" and {field['model_dimension']} > 0"
        constraints = []
        if "choices" in field:
            constraints.append(", ".join(map(str, field["choices"])))
        if field.get("positive"):
            constraints.append("> 0")
        elif "min" in field:
            constraints.append(f">= {field['min']}")
        if "requires" in field:
            constraints.append(f"`{field['requires']}`")
        rows.append(f"| `{key}` | {field.get('parent', '-')} | {visible} | "
                    f"{default} | {' and '.join(constraints)} |")
    rows += ["", "## ABACUS input catalogue", "",
             f"ABACUS revision `{REGISTRY['revision']}` registers {len(PARAMETERS)} keywords. "
             "Unselected catalogue entries are omitted from INPUT. The reader default column "
             "reproduces the native documentation. A callback can also set internal state.", ""]
    def cell(value):
        return " ".join(str(value).split()).replace("|", "\\|")

    for category in sorted({f["category"] for f in PARAMETERS.values()}):
        rows.extend([f"### {category}", "",
                     "| Keyword | Type | Upstream default | Units | Availability | Domain or requirements | Reader reset |",
                     "| --- | --- | --- | --- | --- | --- | --- |"])
        for key, meta in PARAMETERS.items():
            if meta["category"] != category:
                continue
            domain = " ".join(str(meta[k]) for k in ("allowed_values", "value_rule", "requirements") if k in meta)
            row = [f"`{key}`", meta["syntax"], meta["default"], meta.get("unit", ""),
                   meta.get("availability", ""), domain, "yes" if meta.get("reader_reset") else ""]
            rows.append("| " + " | ".join(map(cell, row)) + " |")
        rows.append("")
    return "\n".join(rows).rstrip() + "\n"
