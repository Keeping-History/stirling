from abc import ABC
from dataclasses import dataclass
from pathlib import Path
from typing import List

from dataclasses_json import dataclass_json

from stirling.codecs.base import StirlingMediaCodec
from stirling.containers.base import StirlingMediaContainer
from stirling.plugins.core import StirlingPlugin


@dataclass
@dataclass_json
class StirlingPluginAudioOptions:
    source: str | Path
    source_stream: int
    codec: StirlingMediaCodec
    container: StirlingMediaContainer
    sample_rate: int
    channels: int
    sample_format: str


@dataclass
class StirlingPluginAudio(StirlingPlugin, ABC):
    """StirlingPluginAudio are for using a source audio-only file or for
    extracting audio from a video file. This file is intended as a long-term
    archival version."""

    name: str = "audio"
    depends_on = None
    options: List[StirlingPluginAudioOptions] = None

    def __post_init__(self):
        if self.options is None:
            raise ValueError("options must be set")

    def cmds(self):
        """Extract audio from a media file."""
        return None

    def outputs(self):
        return None

    ## Extract Audio from file
    def cmd(self):
        if (
            self.audio_source_stream == -1
            and self.plugin_name in job.media_info.preferred
            and job.media_info.preferred[self.plugin_name] is not None
        ):
            self.audio_source_stream = job.media_info.preferred[
                self.plugin_name
            ]

        # Set the options to extract audio from the source file.
        options = {
            "hide_banner": True,
            "y": True,
            "loglevel": "quiet",
            "i": job.media_info.source,
            "f": self.audio_output_format[0],
            "map": "0:a:{}".format(self.audio_source_stream),
        }

        output_directory = job.output_directory / self.plugin_name
        output_directory.mkdir(parents=True, exist_ok=True)
        output_file = output_directory / (
            "source.{}".format(self.audio_output_format[1])
        )

        job.commands.append(
            definitions.StrilingCmd(
                plugin_name=self.plugin_name,
                command="ffmpeg {} {}".format(
                    args.ffmpeg_unparser.unparse(**options), output_file
                ),
                priority=self.priority,
                expected_output=output_file,
                depends_on=self.depends_on,
            )
        )
