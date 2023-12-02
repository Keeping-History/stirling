import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from stirling.codecs.audio.base import StirlingMediaCodecAudioBase
from stirling.codecs.base import get_codec
from stirling.command.base import StirlingCommand
from stirling.config import StirlingConfig
from stirling.containers.base import StirlingMediaContainer, get_container
from stirling.job import StirlingJob
from stirling.plugins.core import StirlingPlugin, StirlingPluginOptions


def get_plugin():
    return StirlingPluginAudio()


class StirlingPluginAudioOptions(StirlingPluginOptions):
    source: str | Path | None = None
    source_stream: int | None = None
    plugin_name: str = "audio"
    codec: str | StirlingMediaCodecAudioBase = None
    container: str | StirlingMediaContainer = None
    output_directory: Path | str | None = None
    filename: str | None = None
    start_time: float | None = None
    end_time: float | None = None


@dataclass(kw_only=True)
class StirlingPluginAudio(StirlingPlugin):
    """StirlingPluginAudio extracts the audio from a source file."""

    name: str = "audio"
    depends_on = None
    options: StirlingPluginAudioOptions | str | dict | None = None

    def __post_init__(self):
        super().__post_init__()
        self._counter: int = 0

        self.options: StirlingPluginAudioOptions = (
            StirlingPluginAudioOptions.parse_options(self.options)
        )

        if type(self.options.codec) is str:
            self.options.codec = get_codec(self.options.codec)

        if type(self.options.container) is str:
            self.options.container = get_container(self.options.container)

    def cmds(self, job: StirlingJob):
        """Extract audio from a media file."""
        self._counter += 1

        return [
            StirlingCommand(
                name=f"audio_{self._counter}",
                dependency=job.framework.options.dependencies.get(job.framework.name),
                expected_outputs=[self._cmd_output(job)],
            )
        ]

    def _cmd_output(self, job: StirlingJob):
        return Path(
            job.options.output_directory.resolve()
            / f"audio_{str(self._counter)}-{self.options.codec.output_name}.{self.options.container.file_extension}"
        )

    ## Extract Audio from file
    # def cmd(self):
    #     if (
    #         self.audio_source_stream == -1
    #         and self.plugin_name in job.media_info.preferred
    #         and job.media_info.preferred[self.plugin_name] is not None
    #     ):
    #         self.audio_source_stream = job.media_info.preferred[
    #             self.plugin_name
    #         ]
    #
    #     # Set the options to extract audio from the source file.
    #     options = {
    #         "hide_banner": True,
    #         "y": True,
    #         "loglevel": "quiet",
    #         "i": job.media_info.source,
    #         "f": self.audio_output_format[0],
    #         "map": "0:a:{}".format(self.audio_source_stream),
    #     }
    #
    #     output_directory = job.output_directory / self.plugin_name
    #     output_directory.mkdir(parents=True, exist_ok=True)
    #     output_file = output_directory / (
    #         "source.{}".format(self.audio_output_format[1])
    #     )
    #
    #     job.commands.append(
    #         definitions.StrilingCmd(
    #             plugin_name=self.plugin_name,
    #             command="ffmpeg {} {}".format(
    #                 args.ffmpeg_unparser.unparse(**options), output_file
    #             ),
    #             priority=self.priority,
    #             expected_output=output_file,
    #             depends_on=self.depends_on,
    #         )
    #     )
