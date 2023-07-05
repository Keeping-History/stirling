from pydantic.dataclasses import dataclass

from stirling.core import StirlingClass


@dataclass
class StirlingMediaCodec(StirlingClass):
    name: str
