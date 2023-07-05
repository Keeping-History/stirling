from typing import Dict

from stirling.frameworks.ffmpeg.constants import (
    FFMpegCommandFlags as CmdFlags,
)


def trim_start_end(
    start: str | int | float,
    end: str | int | float,
) -> Dict[str, str]:
    """Trim the media file to a specific start and end time."""
    return {
        CmdFlags.StartTime: f"{start}",
        CmdFlags.EndTime: f"{end}",
        CmdFlags.AccurateSeek: True,
    }
