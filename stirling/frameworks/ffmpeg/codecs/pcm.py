from pydantic.dataclasses import dataclass

from stirling.codecs.audio.pcm import StirlingMediaCodecAudioPCM


@dataclass
class StirlingFFMpegCodecAudioPCM(StirlingMediaCodecAudioPCM):
    def get(self):
        args = {
            "c:a": f"{self.format}{self.sample_format}",
            "ar": self.sample_rate,
            "ac": self.channels,
            "b:a": self.bitrate,
            "map": f"0:a:{self.stream}" if self.stream is not None else None,
        }

        return {k: v for k, v in args.items() if v is not None}
