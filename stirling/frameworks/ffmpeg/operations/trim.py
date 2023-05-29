from typing import Dict

from stirling.frameworks.ffmpeg.constants import (
    FFMpegCommandFlags as CmdFlags,
)


def trim_start_end(
    time_start: str | int | float,
    time_end: str | int | float,
) -> Dict[str, str]:
    """Trim the media file to a specific start and end time."""
    return {
        CmdFlags.StartTime: f"{time_start}",
        CmdFlags.EndTime: f"{time_end}",
        CmdFlags.AccurateSeek: True,
    }
