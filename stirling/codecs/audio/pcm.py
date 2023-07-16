from stirling.codecs.audio.base import StirlingMediaCodecAudioBase
from pydantic.dataclasses import dataclass

from stirling.codecs.base import StirlingMediaCodecEncodingMode


@dataclass
class StirlingMediaCodecAudioPCM(StirlingMediaCodecAudioBase):
    """PCM audio codec."""

    name: str = "pcm"
    description: str = "PCM (Pulse-code modulation)"
    mode: StirlingMediaCodecEncodingMode = StirlingMediaCodecEncodingMode.CBR
    sample_bit_depth: int | None = None
