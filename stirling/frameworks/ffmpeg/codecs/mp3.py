from pydantic.dataclasses import dataclass

from stirling.codecs.audio.mp3 import StirlingMediaCodecAudioMP3
from stirling.config import StirlingConfig
from stirling.frameworks.ffmpeg.constants import FFMpegCommandFlags as FC
from stirling.frameworks.ffmpeg.core import StirlingMediaFrameworkFFMpeg


@dataclass(kw_only=True)
class StirlingFFMpegMediaCodecAudioMP3(StirlingMediaCodecAudioMP3):
    framework: StirlingMediaFrameworkFFMpeg | None = None

    def __post_init__(self):
        super().__post_init__()

        if self.framework is None:
            self._framework = StirlingMediaFrameworkFFMpeg()
        else:
            self._framework = self.framework

        self.framework = self._framework.__class__.__name__

        config_client = StirlingConfig()
        if (
            self.sample_rate
            not in config_client.get("frameworks/ffmpeg/audio/sample_rates")
            or self.sample_rate is None
        ):
            self.sample_rate = config_client.get("audio/defaults/sample_rate")

        default_encoder = config_client.get(
            "frameworks/ffmpeg/audio/encoders/mp3/defaults/encoder_library"
        )

        self._get_encoders(config_client)

        if self.encoder not in [encoder.name for encoder in self.encoders]:
            self.encoder = default_encoder

    def _get_encoders(self, config_client):
        all_encoders = self._framework.capabilities.codecs

        if self.encoders is None:
            self.encoders = []
            encoder_libraries = [
                codec_i for codec_i in all_encoders if codec_i.name == "mp3"
            ]

            for v in encoder_libraries:
                self.encoders.extend(l for l in v.libraries if l.encode == True)

    def get(self):
        args = {
            FC.AUDIO_CODEC: f"{self.encoder}",
            FC.AUDIO_SAMPLE_RATE: self.sample_rate or None,
            FC.AUDIO_CHANNEL_LAYOUT: "+".join(self.channel_layout)
            if self.channel_layout
            else None,
            FC.AUDIO_BITRATE: self.bitrate or None,
            FC.CHANNEL_MAP: f"0:a:{self.stream}" if self.stream else None,
        }

        return {k: v for k, v in args.items() if v is not None}
