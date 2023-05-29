from pathlib import Path
from typing import Any
from uuid import UUID


class StirlingPydanticValidators:
    @staticmethod
    def validate_pure_posix_path(path_to_check: Any) -> Path:
        """Attempt to validate if an object is a valid Path."""
        return Path(path_to_check)

    @staticmethod
    def validate_uuid(this_uuid: Any) -> bool:
        """Attempt to validate whether an object is a valid UUID."""
        try:
            UUID(str(this_uuid))
            return True
        except ValueError:
            return False
