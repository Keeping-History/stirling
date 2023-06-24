from enum import auto
from pathlib import Path
from urllib.parse import urlparse

from strenum import LowercaseStrEnum

default_refresh_period = 5.0


def progress(output: str | Path, refresh: float | int | None) -> str | None:
    refresh_option = f"-stats_period {refresh or default_refresh_period}"

    if isinstance(output, Path) or output.startswith("pipe:"):
        return f"-progress {str(output)} {refresh_option}"

    try:
        output = urlparse(output)
    except ValueError:
        return None

    match output.scheme:
        case "tcp":
            return f"-progress tcp://{output.netloc} {refresh_option}"
        case _:
            pass

    return


def overwrite(overwrite_value: bool) -> str:
    return "-y" if overwrite_value else "-n"


class LogLevel(LowercaseStrEnum):
    QUIET = auto()
    PANIC = auto()
    FATAL = auto()
    ERROR = auto()
    WARNING = auto()
    INFO = auto()
    VERBOSE = auto()
    DEBUG = auto()
    TRACE = auto()


def log_level(
        level: LogLevel,
        hide_repeated_messages: bool = False,
) -> str:
    options: str = ""

    if hide_repeated_messages:
        options += "+repeat"

    options += f"+level+{level.value}"
    return f"-loglevel {options}"


# 7.4 Video size
# Specify the size of the sourced video, it may be a string of the form
# widthxheight, or the name of a size abbreviation.
#
# The following abbreviations are recognized:
#
# ‘ntsc’
# 720x480
#
# ‘pal’
# 720x576
#
# ‘qntsc’
# 352x240
#
# ‘qpal’
# 352x288
#
# ‘sntsc’
# 640x480
#
# ‘spal’
# 768x576
#
# ‘film’
# 352x240
#
# ‘ntsc-film’
# 352x240
#
# ‘sqcif’
# 128x96
#
# ‘qcif’
# 176x144
#
# ‘cif’
# 352x288
#
# ‘4cif’
# 704x576
#
# ‘16cif’
# 1408x1152
#
# ‘qqvga’
# 160x120
#
# ‘qvga’
# 320x240
#
# ‘vga’
# 640x480
#
# ‘svga’
# 800x600
#
# ‘xga’
# 1024x768
#
# ‘uxga’
# 1600x1200
#
# ‘qxga’
# 2048x1536
#
# ‘sxga’
# 1280x1024
#
# ‘qsxga’
# 2560x2048
#
# ‘hsxga’
# 5120x4096
#
# ‘wvga’
# 852x480
#
# ‘wxga’
# 1366x768
#
# ‘wsxga’
# 1600x1024
#
# ‘wuxga’
# 1920x1200
#
# ‘woxga’
# 2560x1600
#
# ‘wqsxga’
# 3200x2048
#
# ‘wquxga’
# 3840x2400
#
# ‘whsxga’
# 6400x4096
#
# ‘whuxga’
# 7680x4800
#
# ‘cga’
# 320x200
#
# ‘ega’
# 640x350
#
# ‘hd480’
# 852x480
#
# ‘hd720’
# 1280x720
#
# ‘hd1080’
# 1920x1080
#
# ‘2k’
# 2048x1080
#
# ‘2kflat’
# 1998x1080
#
# ‘2kscope’
# 2048x858
#
# ‘4k’
# 4096x2160
#
# ‘4kflat’
# 3996x2160
#
# ‘4kscope’
# 4096x1716
#
# ‘nhd’
# 640x360
#
# ‘hqvga’
# 240x160
#
# ‘wqvga’
# 400x240
#
# ‘fwqvga’
# 432x240
#
# ‘hvga’
# 480x320
#
# ‘qhd’
# 960x540
#
# ‘2kdci’
# 2048x1080
#
# ‘4kdci’
# 4096x2160
#
# ‘uhd2160’
# 3840x2160
#
# ‘uhd4320’
# 7680x4320
#
# 7.5 Video rate
# Specify the frame rate of a video, expressed as the number of frames
# generated per second. It has to be a string in the format
# frame_rate_num/frame_rate_den, an integer number, a float number or a valid
# video frame rate abbreviation.
#
# The following abbreviations are recognized:
#
# ‘ntsc’
# 30000/1001
#
# ‘pal’
# 25/1
#
# ‘qntsc’
# 30000/1001
#
# ‘qpal’
# 25/1
#
# ‘sntsc’
# 30000/1001
#
# ‘spal’
# 25/1
#
# ‘film’
# 24/1
#
# ‘ntsc-film’
# 24000/1001
