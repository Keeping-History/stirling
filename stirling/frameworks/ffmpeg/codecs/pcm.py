from pydantic.dataclasses import dataclass
from stirling.codecs.audio.pcm import StirlingMediaCodecAudioPCM
from stirling.config import StirlingConfig
from stirling.frameworks.ffmpeg.core import StirlingMediaFrameworkFFMpeg


@dataclass(kw_only=True)
class StirlingFFMpegMediaCodecAudioPCM(StirlingMediaCodecAudioPCM):
    framework: StirlingMediaFrameworkFFMpeg | None = None

    def __post_init__(self):
        super().__post_init__()

        if self.framework is None:
            self._framework = StirlingMediaFrameworkFFMpeg()
        else:
            self._framework = self.framework
        self.framework = self._framework.__class__.__name__

        config_client = StirlingConfig()
        defaults = config_client.get(
            "frameworks/ffmpeg/audio/encoders/pcm/defaults"
        )

        default_encoder = config_client.get(
            "frameworks/ffmpeg/audio/encoders/defaults/pcm"
        )

        self.encoder = self.encoder or default_encoder

        sample_bit_depths = config_client.get(
            "frameworks/ffmpeg/audio/encoders/pcm/sample_bit_depths"
        )

        if (
            self.sample_bit_depth not in sample_bit_depths
            or self.sample_bit_depth is None
        ):
            self.sample_bit_depth = defaults.get("sample_bit_depth")

        self.encoders = self._get_encoders()

        if self.encoder not in [encoder.name for encoder in self.encoders]:
            self.encoder = default_encoder

    def _get_encoders(self):
        all_codecs = self._framework.capabilities.codecs
        available_codecs = [
            codec_i
            for codec_i in all_codecs
            if codec_i.name.__contains__("pcm")
            and (
                str(self.sample_bit_depth) in codec_i.name
                or not any(char.isdigit() for char in codec_i.name)
            )
        ]

        for codec_i, codec_v in enumerate(available_codecs):
            for library_v in codec_v.libraries:
                if not library_v.encode:
                    available_codecs[codec_i].libraries.remove(library_v)

        return available_codecs

    def get(self):
        args = {
            "c:a": f"{self.encoder}",
            "ar": self.sample_rate,
            "ac": "+".join(self.channel_layout)
            if self.channel_layout
            else None,
            "b:a": self.bitrate,
            "map": f"0:a:{self.stream}" if self.stream is not None else None,
        }

        return {k: v for k, v in args.items() if v is not None}