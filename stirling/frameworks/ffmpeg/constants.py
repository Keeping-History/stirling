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


# -copyts copy timestamps
# -copytb mode copy input stream time base when stream copying
# -xerror error exit on error


class FFMpegCommandFlags(StirlingClass):
    LOG_LEVEL = "-v"
    REPORT = "-report"
    STATS = "-stats"
    BENCHMARKING = "-benchmark_all"
    TIME_LIMIT = "-timelimit"
    TIMESTAMPS = "-debug_ts"
    STATS_FILE = "-vstats_file"

    PROGRESS_NOTIFY = "-progress"
    OVERWRITE = "-y"
    NEVER_OVERWRITE = "-n"

    HIDE_BANNER = "-hide_banner"

    START_TIME = "-ss"
    END_TIME = "-to"
    DURATION = "-t"
    ACCURATE_SEEK = "-accurate_seek"
    CHANNEL_MAP = "map"

    VIDEO_FILTER = "-vf"
    VIDEO_CODEC = "-vcodec"
    VIDEO_BITRATE = "-b:v"
    VIDEO_DISCARD = "-vn"
    VIDEO_ASPECT_RATIO = "-aspect"
    VIDEO_SIZE = "-s"  # (WxH or abbreviation
    VIDEO_FRAME_RATE = "-r"  # (Hz value, fraction or abbreviation)

    AUDIO_CODEC = "-acodec"
    AUDIO_DISCARD = "-an"
    AUDIO_QUALITY_PRESET = "-aq"
    AUDIO_BITRATE = "-b:a"
    AUDIO_SAMPLE_RATE = "-ar"
    AUDIO_SAMPLE_FORMAT = "-sample_fmt"
    AUDIO_CHANNEL_LAYOUT = "-ar"
    AUDIO_CHANNEL_COUNT = "-ac"
    AUDIO_VOLUME_LEVEL = "-vol"

    SUBTITLE_DISCARD = "-sn"

    DATA_DISCARD = "-dn"


@dataclass
class FFMpegCommandValueDimensions(StirlingClass):
    """FFMpeg command value dimensions.

    Note: the dimensions are in the order of
    width, height.

    """

    width: int | str
    height: int | str
    start_x: int | str | None = None
    start_y: int | str | None = None

    def get(self) -> str:
        if self.start_x is not None and self.start_y is not None:
            return f"{self.width}:{self.height}:{self.start_x}:{self.start_y}"
        return f"{self.width}:{self.height}"
