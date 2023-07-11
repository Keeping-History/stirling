from stirling.codecs.base import (
    StirlingMediaCodecEncodingMode,
)
from stirling.codecs.audio.base import StirlingMediaCodecAudioBase
from pydantic.dataclasses import dataclass

from stirling.config import StirlingConfig


@dataclass
class StirlingMediaCodecAudioMP3(StirlingMediaCodecAudioBase):
    """MP3 audio codec."""

    description: str = "MP3 (MPEG audio layer 3)"
    name: str = "mp3"
    mode: StirlingMediaCodecEncodingMode | None = None

    def __post_init__(self):
        config_client = StirlingConfig()
        default_encoder = config_client.get("audio/codecs/mp3/defaults/encoder")

        self.encoders = config_client.get("audio/codecs/mp3/encoders")

        if self.encoder:
            self.encoder = (
                self.encoder
                if self.encoder in self.encoders
                else default_encoder
            )
        else:
            self.encoder = default_encoder

        super().__post_init__()
