from typing import Dict

from stirling.frameworks.ffmpeg.constants import (
    FFMpegCommandFlags as CmdFlags,
)


def audio_only() -> Dict[str, bool]:
    """Trim the media file to a specific start and end time."""
    return {
        CmdFlags.VIDEO_DISCARD: True,
        CmdFlags.SUBTITLE_DISCARD: True,
        CmdFlags.DATA_DISCARD: True,
    }
