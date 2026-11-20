"""Generate the installable catalogue from a native ABACUS registry dump."""
import argparse
import json
import re
from pathlib import Path

import yaml


def catalogue(dump, revision):
    documented = {row["name"]: row for row in dump["parameters"]}
    registry = dump["registry"]
    if documented.keys() - registry.keys() or len(documented) != len(dump["parameters"]):
        raise ValueError("Inconsistent native registration and documentation lists")
    fields = {}
    for name, native in registry.items():
        doc = documented.get(name, {})
        field = {
            "category": doc.get("category", "Additional registered inputs"),
            "syntax": doc.get("type", native["kind"]),
            "kind": native["kind"], "scalar": native["scalar"],
            "description": doc.get("description") or native.get("annotation", ""),
            "default": str(doc.get("default_value", native.get("initial", ""))),
        }
        for key in ("unit", "availability", "value_rule", "allowed_values", "requirements"):
            if doc.get(key):
                field[key] = doc[key]
        if native["reset"]:
            field["reader_reset"] = True
        if "initial" in native:
            field["initial"] = native["initial"]
        if not doc:
            field["documented"] = False
        fields[name] = field
    return {"upstream": "deepmodeling/abacus-develop", "revision": revision, "parameters": fields}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dump", type=Path)
    parser.add_argument("revision", help="full ABACUS git commit")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.revision):
        parser.error("Provide the full upstream Git revision")
    path = Path(__file__).resolve().parents[1] / "abacus_kit/catalog.json"
    data = catalogue(yaml.safe_load(args.dump.read_text()), args.revision)
    generated = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if generated != path.read_text():
            parser.exit(1, "The packaged catalogue differs from the native registry.\n")
    else:
        path.write_text(generated)
    print(f"{len(data['parameters'])} registered keywords at {args.revision}")
