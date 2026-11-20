"""Read model metadata with the user's DeePMD installation."""
import json
import subprocess
from functools import lru_cache


_INSPECT = """
import json, sys
from deepmd.infer import DeepPot
model = DeepPot(sys.argv[1])
print(json.dumps([list(model.get_type_map()), int(model.get_dim_fparam()), int(model.get_dim_aparam())]))
"""


@lru_cache(maxsize=4)
def inspect_model(python, path, mtime_ns, size):
    # Modification time and size are part of the cache key for replaced models.
    result = subprocess.run([python, "-c", _INSPECT, str(path)], text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise ValueError("DeePMD could not open the model: " + result.stderr[-650:])
    species, frames, atoms = json.loads(result.stdout.strip().splitlines()[-1])
    return species, int(frames), int(atoms)
