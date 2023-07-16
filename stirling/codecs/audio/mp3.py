from stirling.codecs.base import (
    StirlingMediaCodecEncodingMode,
)
from stirling.codecs.audio.base import StirlingMediaCodecAudioBase
from pydantic.dataclasses import dataclass


@dataclass
class StirlingMediaCodecAudioMP3(StirlingMediaCodecAudioBase):
    """MP3 audio codec."""

    description: str = "MP3 (MPEG audio layer 3)"
    name: str = "mp3"
    mode: StirlingMediaCodecEncodingMode | None = (
        StirlingMediaCodecEncodingMode.VBR
    )
