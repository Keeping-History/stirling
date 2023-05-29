from pathlib import Path
from typing import List, Union

from stirling.dependencies import StirlingDependency
from stirling.frameworks.ffmpeg.probe import StirlingMediaFrameworkFFMpegProbe


def get_video_letterbox_detect(
    transcoder: StirlingDependency,
    probe: StirlingDependency,
    source: Union[str, Path],
    stream_id: int,
    options: dict = None,
) -> List[int]:
    if options is None:
        options = {}
    probe_detect_value = StirlingMediaFrameworkFFMpegProbe(
        source,
        options,
        transcoder,
        probe,
    ).letterbox_detect(stream_id)

    if len(probe_detect_value) != 4:
        raise ValueError("Could not auto-detect crop area.")

    return probe_detect_value
