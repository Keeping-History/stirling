from pydantic.dataclasses import dataclass

from stirling.codecs.audio.mp3 import StirlingMediaCodecAudioMP3
from stirling.config import StirlingConfig
from stirling.frameworks.ffmpeg.constants import FFMpegCommandFlags as FC
from stirling.frameworks.ffmpeg.core import StirlingMediaFrameworkFFMpeg


@dataclass(kw_only=True)
class StirlingFFMpegMediaCodecAudioMP3(StirlingMediaCodecAudioMP3):
    framework: StirlingMediaFrameworkFFMpeg | None = None

    def __post_init__(self):
        if self.framework is None:
            self.framework = StirlingMediaFrameworkFFMpeg()

        config_client = StirlingConfig()

        all_encoders = self.framework.capabilities.codecs
        default_encoder = config_client.get(
            "frameworks/ffmpeg/audio/encoders/defaults/mp3"
        )

        if (
            self.sample_rate
            not in config_client.get("frameworks/ffmpeg/audio/sample_rates")
            or self.sample_rate is None
        ):
            self.sample_rate = config_client.get("audio/defaults/sample_rate")

        if self.encoders is None:
            self.encoders = []
            encoder_libraries = [
                codec_i for codec_i in all_encoders if codec_i.name == "mp3"
            ]

            for v in encoder_libraries:
                self.encoders.extend(l for l in v.libraries if l.encode == True)

        if self.encoder not in [encoder.name for encoder in self.encoders]:
            self.encoder = default_encoder

        super().__post_init__()

    def get(self):
        args = {
            FC.AUDIO_STREAM_MAP: f"{self.encoder}",
            FC.AUDIO_SAMPLE_RATE: self.sample_rate or None,
            FC.AUDIO_CHANNEL_LAYOUT: "+".join(self.channel_layout)
            if self.channel_layout
            else None,
            FC.AUDIO_BITRATE: self.bitrate or None,
            "map": f"0:a:{self.stream}" if self.stream else None,
        }

        return {k: v for k, v in args.items() if v is not None}
