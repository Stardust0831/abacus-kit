"""Read native keyword metadata and evaluate its applicability conditions."""
import json
import math
import operator
import re
from functools import lru_cache
from pathlib import Path

import pyparsing as pp


REGISTRY = json.loads(Path(__file__).with_name("catalog.json").read_text())
PARAMETERS = REGISTRY["parameters"]
YES = {"true", "1", "t", "yes", "y", "on", ".true."}
NO = {"false", "0", "f", "no", "n", "off", ".false."}
COMPARE = {"==": operator.eq, "!=": operator.ne, ">": operator.gt, "<": operator.lt,
           ">=": operator.ge, "<=": operator.le}
word = pp.Regex(r"[A-Za-z0-9_.+\-]+")
operands = pp.Group(pp.Suppress("[") + pp.DelimitedList(word) + pp.Suppress("]") | word)
comparison = pp.Group(word + pp.one_of("== != >= <= > < contains in") + operands)
grammar = pp.infix_notation(comparison, [(pp.Keyword("and"), 2, pp.OpAssoc.LEFT),
                                         (pp.Keyword("or"), 2, pp.OpAssoc.LEFT)])


@lru_cache(maxsize=None)
def condition(source):
    return grammar.parse_string(source, parse_all=True)[0].as_list()


def number(token, integer=False):
    if integer and not re.fullmatch(r"[+-]?[0-9]+", token):
        raise ValueError(f"Expected an integer, got {token!r}")
    value = int(token) if integer else float(token)
    if not math.isfinite(value) or (integer and not -(2**31) <= value < 2**31):
        raise ValueError(f"Value outside the supported range: {token}")
    return value


def boolean(token):
    token = token.lower()
    if token in YES | NO:
        return token in YES
    raise ValueError(f"Expected a boolean, got {token!r}")


def converted(actual, token):
    if isinstance(actual, bool):
        return boolean(token)
    if isinstance(actual, (float, int)):
        if token in {"true", "false"}:
            return int(boolean(token))
        return float(token)
    return token


def matches(tree, values):
    """Three-valued comparison: None denotes a prerequisite resolved by the reader."""
    key, op = tree[:2]
    if op in ("and", "or"):
        results = [matches(part, values) for part in tree[::2]]
        decisive = op == "or"
        if decisive in results:
            return decisive
        return None if None in results else not decisive
    actual = values.get(key)
    if actual is None:
        return None
    literals = tree[2]
    if op == "contains":
        items = actual if isinstance(actual, (list, tuple)) else [actual]
        return any(item == converted(item, literals[0]) for item in items)
    if isinstance(actual, (list, tuple)):
        if not actual:
            return None
        actual = actual[0]
    if op == "in":
        return any(actual == converted(actual, literal) for literal in literals)
    return COMPARE[op](actual, converted(actual, literals[0]))


def applicable(name, context):
    expr = PARAMETERS[name].get("availability")
    # The upstream manual leaves a number of task/solver families unannotated.
    # These gates describe the editor's workflow for those families.
    category = PARAMETERS[name]["category"]
    if name.startswith("lj_") and context.get("esolver_type") != "lj":
        return False
    if name.startswith("msst_") and context.get("md_type") != "msst":
        return False
    if category == "Molecular dynamics" and name.startswith("md_") and context.get("calculation") != "md":
        return False
    if category == "Density functional perturbation theory" and context.get("esolver_type") != "dfpt":
        return False
    return matches(condition(expr), context) if expr else True


def requirements(name):
    for rule in PARAMETERS[name].get("requirements", "").split("; "):
        if rule.startswith("When "):
            when, require = rule[5:].split(": require ")
            yield when, require
        elif rule:
            yield "", rule


REQUIREMENTS = [(name, condition(when) if when else None, require) for name in PARAMETERS
                for when, require in requirements(name)]


def parse(name, raw):
    field = PARAMETERS[name]
    text = str(raw).strip()
    if not text or any(c in str(raw) for c in "\r\n\x00#!") or not text.isascii():
        raise ValueError(f"{name} requires one nonempty ASCII INPUT value without comment markers")
    tokens = text.split()
    kind, syntax = field["kind"], field["syntax"].lower()
    if kind == "tokens" and syntax in ("boolean", "real"):
        kind = {"boolean": "bool", "real": "real"}[syntax]
    if kind == "bool":
        if len(tokens) != 1:
            raise ValueError(f"{name} takes one boolean")
        value = boolean(text)
    elif kind in ("real", "integer"):
        value = number(text, kind == "integer")
    elif kind == "string":
        if len(tokens) != 1:
            raise ValueError(f"{name} takes one token")
        value = text
    elif "optional" in syntax and syntax.startswith(("boolean", "integer")):
        if len(tokens) > 2:
            raise ValueError(f"{name} takes a value and an optional integer")
        first = int(boolean(tokens[0])) if syntax.startswith("boolean") else number(tokens[0], True)
        value = [first] + [number(token, True) for token in tokens[1:]]
    elif kind in ("integer_vector", "real_vector") or syntax == "integer integer integer":
        integers = kind == "integer_vector" or syntax == "integer integer integer"
        # Certain ABACUS vector readers accept N*value. Keep the spelling for
        # the target reader, whose per-key input syntax is authoritative.
        if any("*" in token for token in tokens):
            for token in tokens:
                count, star, item = token.partition("*")
                if star and not re.fullmatch(r"[1-9][0-9]*", count):
                    raise ValueError(f"Invalid repetition in {name}: {token}")
                number(item if star else count, integers)
            value = text
        else:
            value = [number(token, integers) for token in tokens]
            counts = {"three integers": (3,), "integer integer integer": (3,), "real real": (2,),
                      "integer*2": (2,), "vector of real (3 values)": (3,), "vector of real (6 values)": (6,),
                      "vector of integer (4 values)": (4,), "vector of real (1 or 3 values)": (1, 3),
                      "vector of int (1 or 3 values)": (1, 3)}
            if syntax in counts and len(value) not in counts[syntax]:
                raise ValueError(f"{name} expects {field['syntax']}")
            if syntax.startswith("integer followed"):
                value[0] = number(tokens[0], True)
    elif kind == "string_vector":
        value = tokens
    else:
        value = text
    if "allowed_values" in field and value not in field["allowed_values"]:
        raise ValueError(f"{name} accepts {field['allowed_values']}")
    if name == "cell_replica" and (not isinstance(value, list) or any(x <= 0 for x in value)):
        raise ValueError("cell_replica requires three positive integers")
    if field.get("value_rule") and matches(condition(field["value_rule"]), {"value": value}) is False:
        raise ValueError(f"{name} requires {field['value_rule']}")
    return value


@lru_cache(maxsize=1)
def literal_defaults():
    """An initializer is a hint for visibility, never text to insert into INPUT."""
    result = {}
    for name, field in PARAMETERS.items():
        value = field.get("initial")
        if not value or field["kind"] == "tokens":
            continue
        if field["kind"] == "string" and not re.fullmatch(r"[\w.+-]+", value):
            continue
        try:
            result[name] = parse(name, value)
        except (ValueError, OverflowError):
            continue
    return result


def details(name):
    field = PARAMETERS[name]
    lines = [f"{name}  |  {field['category']}", f"Type: {field['syntax']}"]
    for key, label in (("unit", "Unit"), ("default", "ABACUS default"),
                       ("allowed_values", "Choices"), ("value_rule", "Range"),
                       ("availability", "Available when"), ("requirements", "Requirements")):
        if field.get(key):
            lines.append(f"{label}: {field[key]}")
    if field.get("reader_reset"):
        lines.append("ABACUS registers a reset callback for this keyword.")
    if not field.get("documented", True):
        lines.append("Registered in the reader; absent from the upstream keyword manual.")
    return "\n".join(lines + ["", field["description"]])


def search(query="", category=None):
    words = query.casefold().split()
    return [key for key, field in PARAMETERS.items()
            if (not category or field["category"] == category)
            and all(w in key + " " + field["category"].casefold() + " " + field["description"].casefold()
                    for w in words)]
