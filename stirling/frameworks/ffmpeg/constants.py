from typing import Union

from pydantic.dataclasses import dataclass
from strenum import StrEnum

from stirling.core import StirlingClass


class FFMpegDither(StrEnum):
    """Dithering algorithms for FFMpeg.

    Note: not all dithering types work for all
    formats or filters. See the FFMpeg documentation
    for more information.

    """

    OFF = "none"
    AUTO = "auto"
    BAYER = "bayer"
    ERROR_DIFFUSION = "ed"
    ADDITIVE = "a_dither"
    XOR = "x_dither"
    FLOYD_STEINBERG = "fs"


class FFMpegCommandFlags(StirlingClass):
    VIDEO_FILTER = "-vf"
    START_TIME = "-ss"
    END_TIME = "-to"
    DURATION = "-t"
    ACCURATE_SEEK = "-accurate_seek"
    CHANNEL_MAP = "map"
    AUDIO_CODEC = "-c:a"
    VIDEO_CODEC = "-c:v"
    AUDIO_BITRATE = "-b:a"
    AUDIO_SAMPLE_RATE = "-ar"
    AUDIO_CHANNEL_LAYOUT = "-ar"


@dataclass
class FFMpegCommandValueDimensions(StirlingClass):
    """FFMpeg command value dimensions.

    Note: the dimensions are in the order of
    width, height.

    """

    width: Union[int, str]
    height: Union[int, str]
    start_x: Union[int, str] | None = None
    start_y: Union[int, str] | None = None

    def get(self) -> str:
        if self.start_x is not None and self.start_y is not None:
            return f"{self.width}:{self.height}:{self.start_x}:{self.start_y}"
        return f"{self.width}:{self.height}"
