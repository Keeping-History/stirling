from urllib.parse import urlparse
from pathlib import Path


def progress(output: str | Path, refresh: float | int) -> str:
    if refresh is None:
        default_refresh_period = 5.0
        refresh = default_refresh_period

    if type(refresh) is int:
        refresh = float(refresh)

    refresh_option = f"-stats_period {refresh}"

    if isinstance(output, Path) or output.startswith("pipe:"):
        return f"-progress {str(output)} {refresh_option}"

    try:
        output = urlparse(output)
    except ValueError:
        return ""

    match output.scheme:
        case "tcp":
            return f"-progress tcp://{output.netloc} {refresh_option}"
        case _:
            pass

    return ""


def overwrite(overwrite_value: bool) -> str:
    return "-y" if overwrite_value else "-n"
