from pathlib import Path
from typing import Dict, Tuple

from stirling.frameworks.ffmpeg.constants import (
    FFMpegCommandFlags as CmdFlags,
    FFMpegCommandValueDimensions as CmdDims,
)
from stirling.frameworks.ffmpeg.helpers import get_video_letterbox_detect
from stirling.frameworks.media_info import (
    StirlingStreamVideo,
)


def crop_w_h_x_y(
    width: int,
    height: int,
    start_x: int,
    start_y: int,
) -> Dict[str, str]:
    """Crop the video to a specific width, height, and starting position."""
    return {
        f"{CmdFlags.VideoFilter}": f"crop="
        f"{CmdDims(width, height, start_x, start_y).get()}"
    }


def crop_ratio(ratio: Tuple[int, int]) -> Dict[str, str]:
    """Crop the video to a specific ratio/scale."""
    width, height = f"ih/{ratio[0] * ratio[1]}", "ih"
    return {f"{CmdFlags.VideoFilter}": f"crop={CmdDims(width, height).get()}"}


def crop_ratio_x_y(
    ratio: Tuple[int, int],
    position: Tuple[int, int],
) -> Dict[str, str]:
    """Crop the video to a specific ratio/scale, with a starting
    position."""
    return {
        f"{CmdFlags.VideoFilter}": f"crop=ih/{ratio[0] * ratio[1]}:ih:"
        f"{position[0]}:{position[1]}"
    }


def crop(self, source: Path, stream: StirlingStreamVideo) -> Dict[str, str]:
    """Crop the video using the black-bar auto-detection feature of
    FFMpeg."""
    box = get_video_letterbox_detect(
        self._binary_transcoder,
        self._binary_probe,
        source,
        stream.stream_id,
        self._default_cmd_options,
    )

    if len(box) != 4:
        raise ValueError("Could not auto-detect crop area.")
    return {f"{CmdFlags.VideoFilter}": f"crop={CmdDims(*box).get()}"}
