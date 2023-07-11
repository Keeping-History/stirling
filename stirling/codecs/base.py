from typing import List

from pydantic.dataclasses import dataclass
from strenum import StrEnum

from stirling.core import StirlingClass


@dataclass
class StirlingMediaCodec(StirlingClass):
    name: str
    description: str | None = None
    stream: int | None = None
    encoder: str | None = None
    encoders: List | None = None


class StirlingMediaCodecEncodingMode(StrEnum):
    CBR = "cbr"
    VBR = "vbr"
    ABR = "abr"


class StirlingMediaCodecQualityLevel(StrEnum):
    level0 = "0"
    level1 = "1"
    level2 = "2"
    level3 = "3"
    level4 = "4"
    level5 = "5"
    level6 = "6"
    level7 = "7"
    level8 = "8"
    level9 = "9"


class StirlingMediaCodecQualityLevelName(StrEnum):
    low = StirlingMediaCodecQualityLevel.level0
    medium = StirlingMediaCodecQualityLevel.level5
    high = StirlingMediaCodecQualityLevel.level9


@dataclass
class StirlingMediaCodecVideoBase(StirlingClass):
    name: str
