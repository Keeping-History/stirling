from typing import Dict, Tuple

from stirling.frameworks.ffmpeg.constants import (
    FFMpegCommandFlags as CmdFlags,
    FFMpegCommandValueDimensions as CmdDims,
)


def resize_w_h(width: int, height: int) -> Dict[str, str]:
    """Resize the video to a specific width and height."""
    return {f"{CmdFlags.VideoFilter}": f"scale={CmdDims(width, height).get()}"}


def resize_ratio(ratio: Tuple[int, int]) -> Dict[str, str]:
    """Resize the video to a specific scale/ratio."""
    width, height = f"iw*{ratio[0]}", f"ih*{ratio[1]}"
    return {f"{CmdFlags.VideoFilter}": f"scale={CmdDims(width, height).get()}"}
