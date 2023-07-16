from typing import List

from pydantic.dataclasses import dataclass

from stirling.codecs.base import StirlingMediaCodec
from stirling.config import StirlingConfig


@dataclass
class StirlingMediaCodecAudioBase(StirlingMediaCodec):
    sample_rate: int | None = None
    channel_layout: List | None = None
    bitrate: int | None = None
    output_name: str | None = None
    encoder: str | None = None

    def __post_init__(self):
        config = StirlingConfig().get("audio")
        defaults = config.get("defaults")

        if self.sample_rate is None:
            self.sample_rate = config.get("sample_rate") or None

        if self.bitrate is None:
            self.bitrate = defaults.get("bitrate")

        if self.output_name is None:
            self.output_name = "_".join(
                filter(
                    None,
                    (
                        f"co-{self.encoder}" if self.encoder else None,
                        f"br-{str(self.bitrate)}" if self.bitrate else None,
                        f"sr-{str(self.sample_rate)}"
                        if self.sample_rate
                        else None,
                        f"ch-{len(self.channel_layout)}"
                        if self.channel_layout
                        else None,
                    ),
                )
            )
