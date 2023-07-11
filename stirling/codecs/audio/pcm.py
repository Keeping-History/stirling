from stirling.codecs.audio.base import StirlingMediaCodecAudioBase
from pydantic.dataclasses import dataclass

from stirling.codecs.base import StirlingMediaCodecEncodingMode
from stirling.config import StirlingConfig


@dataclass
class StirlingMediaCodecAudioPCM(StirlingMediaCodecAudioBase):
    """PCM audio codec."""

    name: str = "pcm"
    description: str = "PCM (Pulse-code modulation)"
    mode: StirlingMediaCodecEncodingMode = StirlingMediaCodecEncodingMode.CBR
    sample_bit_depth: int | None = None

    def __post_init__(self):
        config_client = StirlingConfig()
        defaults = StirlingConfig().get("audio/defaults")

        all_encoders = config_client.get("audio/codecs/pcm/encoders")
        default_encoder = config_client.get("audio/codecs/pcm/defaults/encoder")

        if self.sample_bit_depth == 0:
            self.sample_bit_depth = defaults.get("sample_bit_depth")

        self.encoders = [
            codec_i
            for codec_i in all_encoders
            if codec_i.find(str(self.sample_bit_depth)) != -1
            or codec_i.find("law") != -1
            and self.sample_bit_depth == 8
        ]

        if self.encoder:
            self.encoder = (
                self.encoder
                if self.encoder in self.encoders
                else default_encoder
            )
        else:
            self.encoder = default_encoder

        super().__post_init__()
