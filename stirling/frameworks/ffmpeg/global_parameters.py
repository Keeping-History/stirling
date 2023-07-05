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
