from pydantic.dataclasses import dataclass

from stirling.codecs.base import (
    StirlingMediaCodecEncodingMode as EncMode,
    StirlingMediaCodec,
)
from stirling.codecs.video.base import StirlingMediaCodecVideoBase


@dataclass
class StirlingMediaCodecVideoAV1(StirlingMediaCodec, StirlingMediaCodecVideoBase):
    """PCM audio codec."""

    name: str = "av1"
    description: str = "AOMedia Video 1 "
    mode: EncMode = EncMode.CBR
    sample_bit_depth: int | None = None
