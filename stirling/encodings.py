from dataclasses import asdict, is_dataclass
from datetime import datetime
from json import JSONEncoder
from pathlib import Path
from uuid import UUID

from pydantic.validators import _VALIDATORS


class StirlingJSONEncoder(JSONEncoder):
    """StirlingJSONEncoder is a custom JSON encoder for objects that inherit the StirlingClass as a parent."""

    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        elif isinstance(o, UUID):
            return str(o)
        elif isinstance(o, datetime):
            return str(o)
        elif isinstance(o, Path):
            return str(o)
        return super().default(o)


from stirling.typing import StirlingPydanticValidators

_VALIDATORS.extend(
    [
        (Path, [StirlingPydanticValidators.validate_pure_posix_path]),
        (UUID, [StirlingPydanticValidators.validate_uuid]),
    ]
)
