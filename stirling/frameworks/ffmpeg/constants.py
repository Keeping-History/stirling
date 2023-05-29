from typing import Union

from pydantic.dataclasses import dataclass

from stirling.core import StirlingClass


class FFMpegDither(StirlingClass):
    """Dithering algorithms for FFMpeg.

    Note: not all dithering types work for all
    formats or filters. See the FFMpeg documentation
    for more information.

    """

    Off = "none"
    Auto = "auto"
    Bayer = "bayer"
    ErrorDiffusion = "ed"
    Additive = "a_dither"
    Xor = "x_dither"
    FloydSteinberg = "fs"


class FFMpegCommandFlags(StirlingClass):
    VideoFilter = "-vf"
    StartTime = "-ss"
    EndTime = "-to"
    Duration = "-t"
    AccurateSeek = "-accurate_seek"


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
