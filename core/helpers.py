import json
import shutil
import uuid
import dataclasses
from datetime import datetime
from pathlib import Path


def check_dependencies_binaries(required_binaries: list) -> bool:
    required_binaries_missing = []
    for program in required_binaries:
        if shutil.which(program) is None:
            required_binaries_missing.append(program)
    if not len(required_binaries_missing) == 0:
        return "missing binary dependencies: {}".format(
            " ".join(required_binaries_missing)
        )
    return True


def is_valid_uuid(uuid_to_test: str, version: int = 4) -> bool:
    try:
        uuid_obj = uuid.UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test


# The StirlingJobEncoder class is used to serialize the StirlingJob class into JSON.
class StirlingJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if dataclasses.is_dataclass(obj):
            d = dataclasses.asdict(obj)
            return self._remove_hidden_keys(d)
        elif isinstance(obj, uuid.UUID):
            # if the obj is uuid, we simply return the value of uuid
            return str(obj)
        elif isinstance(obj, datetime):
            return str(obj)
        elif isinstance(obj, Path):
            return str(obj)
        return super().default(obj)

    def _remove_hidden_keys(self, _d):
        return {
            a: self._remove_hidden_keys(b) if isinstance(b, dict) else b
            for a, b in _d.items()
            if b and not a.startswith("_")
        }
