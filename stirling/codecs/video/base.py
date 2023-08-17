from pydantic.dataclasses import dataclass

from stirling.config import StirlingConfig


@dataclass
class StirlingMediaCodecVideoBase:
    bitrate: int | None = None
    output_name: str | None = None
    encoder: str | None = None

    def __post_init__(self):
        config = StirlingConfig().get("video")
        defaults = config.get("defaults")

        if self.bitrate is None:
            self.bitrate = defaults.get("bitrate")

        if self.output_name is None:
            self.output_name = "_".join(
                filter(
                    None,
                    (
                        f"co-{self.encoder}" if self.encoder else None,
                        f"br-{str(self.bitrate)}" if self.bitrate else None,
                    ),
                )
            )
