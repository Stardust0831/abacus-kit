"""Check a prepared case with a target ABACUS executable."""
import math
import subprocess

from .catalog import PARAMETERS, boolean


def equivalent(key, wanted, actual):
    kind = PARAMETERS[key]["kind"]
    if wanted.split() == actual.split():
        return True
    if key in ("pseudo_dir", "orbital_dir", "read_file_dir"):
        return wanted.rstrip("/") == actual.rstrip("/")
    if kind in ("real", "real_vector", "integer_vector", "integer"):
        left, right = wanted.split(), actual.split()
        if key in ("kspacing", "dfpt_qmesh") and len(left) == 1 and len(right) == 3:
            left *= 3
        if "optional" in PARAMETERS[key]["syntax"].lower() and left and len(left) < len(right):
            right = right[:len(left)]
        try:
            return len(left) == len(right) and all(
                math.isclose(float(a), float(b), rel_tol=1e-12, abs_tol=0.0)
                for a, b in zip(left, right))
        except ValueError:
            return False
    if kind == "bool":
        return boolean(actual) == boolean(wanted)
    return actual.strip() == wanted


def check_reader(executable, directory, requested):
    def invoke(option):
        return subprocess.run([executable, option], cwd=directory, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True)

    help_text = invoke("--help").stdout
    readback = "--check-input-values" in help_text
    result = invoke("--check-input-values" if readback else "--check-input")
    if result.returncode or "INPUT parameters have been successfully checked" not in result.stdout:
        raise ValueError("ABACUS input check failed\n" + result.stdout[-2500:])
    if not readback:
        return "reader accepted INPUT (value reporting unavailable)"
    reported = {}
    for line in result.stdout.splitlines():
        if line.startswith("INPUT_VALUE\t"):
            _, key, value = line.split("\t", 2)
            reported[key] = value.strip()
    for key, wanted in requested.items():
        actual = reported.get(key)
        if actual is None or not equivalent(key, wanted, actual):
            raise ValueError(f"ABACUS readback for {key}: requested {wanted}, reported {actual}")
    return f"verified {len(requested)} explicit values"
