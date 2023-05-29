from pathlib import Path
from uuid import UUID

from pydantic.validators import _VALIDATORS

from stirling.typing import StirlingPydanticValidators

_VALIDATORS.extend(
    [
        (Path, [StirlingPydanticValidators.validate_pure_posix_path]),
        (UUID, [StirlingPydanticValidators.validate_uuid]),
    ]
)
