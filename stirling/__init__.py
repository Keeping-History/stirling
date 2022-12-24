
from typing import Any
import pathlib

from pydantic.validators import _VALIDATORS

def validate_pure_posix_path(v: Any) -> pathlib.Path:
    """Attempt to convert a value to a Path"""
    return pathlib.Path(v)


_VALIDATORS.append((pathlib.Path, [validate_pure_posix_path]))
