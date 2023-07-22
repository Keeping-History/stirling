from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import dataclass_json
from pydantic import BaseModel

from stirling.command.base import StirlingCommand
from stirling.config import StirlingConfig
from stirling.job import StirlingJob
from stirling.plugins.core import StirlingPlugin, StirlingPluginOptions


@dataclass
@dataclass_json
class StirlingPluginAudioOptions(BaseModel, StirlingPluginOptions):
    source: str | Path
    source_stream: int
    codec: str
    container: str
    output_directory: Path | str | None = None
    filename: str | None = None
    start_time: float | None = None
    end_time: float | None = None


@dataclass
@dataclass
class StirlingPluginAudio(StirlingPlugin):
    """StirlingPluginAudio extracts the audio from a source file."""

    name: str = "audio"
    depends_on = None
    options: StirlingPluginAudioOptions | str | dict = None

    def __post_init__(self):
        self.output = []
        self.commands = []

        if type(self.options) is str:
            try:
                self.options = StirlingPluginAudioOptions.parse_raw(
                    self.options
                )
            except Exception as e:
                raise ValueError(
                    "options must be a valid StirlingPluginAudioOptions"
                ) from e
        if type(self.options) is dict:
            try:
                self.options = StirlingPluginAudioOptions.parse_obj(
                    self.options
                )
            except Exception as e:
                raise ValueError(
                    "options must be a valid StirlingPluginAudioOptions"
                ) from e
        if self.options is None:
            raise ValueError(
                "options must be a valid StirlingPluginAudioOptions"
            )

        config_client = StirlingConfig()
        default_options = config_client.get("plugins/audio/defaults")
        if self.options.codec is None:
            self.options.codec = default_options.get("codec")
        if self.options.container is None:
            self.options.container = default_options.get("container")
        if self.options.output_directory is None:
            self.output_directory = default_options.get("output_directory")
        if self.options.filename is None:
            self.options.filename = default_options.get("filename")

    def cmds(self, job: StirlingJob):
        """Extract audio from a media file."""
        if not job.framework.options:
            # TODO: Set a real error here
            return ValueError("Framework options must be set.")
        print(self.options.codec)
        print(job.framework.capabilities.codecs)
        self.outputs(job)
        self.commands = [
            StirlingCommand(
                name="audio",
                dependency=job.framework.options.dependencies.get(
                    job.framework.name
                ),
                arguments={},
                expected_outputs=self.output,
            )
        ]

        return self.commands

    def outputs(self, job: StirlingJob):
        self.output = [
            f"{self.options.output_directory.resolve()}.{self.options.container}"
        ]
        return self.output

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
