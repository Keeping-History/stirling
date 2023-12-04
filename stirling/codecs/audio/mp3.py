from pydantic.dataclasses import dataclass

from stirling.codecs.audio.base import StirlingMediaCodecAudioBase
from stirling.codecs.base import (
    StirlingMediaCodecEncodingMode as EncMode,
    StirlingMediaCodec,
)


@dataclass
class StirlingMediaCodecAudioMP3(StirlingMediaCodec, StirlingMediaCodecAudioBase):
    """MP3 audio codec."""

    name: str = "mp3"
    description: str = "MP3 (MPEG audio layer 3) Format"
    mode: EncMode | None = EncMode.VBR
