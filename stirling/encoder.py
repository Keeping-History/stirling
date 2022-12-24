from dataclasses import dataclass
from typing import List

from stirling import core

# TODO: Check here for encoders to implement. https://www.loc.gov/preservation/digital/formats/fdd/browse_list.shtml


@dataclass
class StirlingEncoder(core.StirlingClass):
    """StirlingEncoder is a class for handling encoder options.

    Attributes:
        name (str): The name of the encoder. We focus on the name
            of the underlying Video Coding Format (or Video Compression
            Format/Standard, VCF for short) and not the container format or
            codec. For example, we use `AVC` (for h.264 standard video)
            instead of `mp4` or `ts`, or `AV1` instead of `webm` or `mkv`.
        options (dict): A dictionary of options to pass to the encoder.

    """

    name: str
    options: dict
    frameworks: List[str]
    encoder_libraries: List[str]
    encoder_library_default: str
