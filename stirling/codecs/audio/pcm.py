from pydantic.dataclasses import dataclass

from stirling.codecs.audio.base import StirlingMediaCodecAudioBase
from stirling.codecs.base import (
    StirlingMediaCodecEncodingMode as EncMode,
    StirlingMediaCodec,
)


@dataclass
class StirlingMediaCodecAudioPCM(StirlingMediaCodec, StirlingMediaCodecAudioBase):
    """PCM audio codec."""

    name: str = "pcm"
    description: str = "PCM (Pulse-code modulation)"
    mode: EncMode = EncMode.CBR
    sample_bit_depth: int | None = None
