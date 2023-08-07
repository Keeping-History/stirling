from dataclasses import dataclass
from pathlib import Path

from dataclasses_json import dataclass_json
from pydantic import BaseModel

from stirling.command.base import StirlingCommand
from stirling.job import StirlingJob
from stirling.plugins.core import StirlingPlugin, StirlingPluginOptions


@dataclass
@dataclass_json
class StirlingPluginAudioOptions(BaseModel, StirlingPluginOptions):
    source: str | Path
    source_stream: int
    codec: str | None = None
    container: str | None = None
    output_directory: Path | str | None = None
    filename: str | None = None
    start_time: float | None = None
    end_time: float | None = None
    plugin_name: str = "audio"


@dataclass(kw_only=True)
class StirlingPluginAudio(StirlingPlugin):
    """StirlingPluginAudio extracts the audio from a source file."""

    name: str = "audio"
    depends_on = None
    options: StirlingPluginAudioOptions | str | dict

    def __post_init__(self):
        self._counter: int = 0

        self.logger.debug(f"Initializing {self.name}")
        self.logger.debug(f"Pre-parse options: {type(self.options)} - {self.options}")

        self.options: StirlingPluginAudioOptions = self._parse_options(self.options)

        self.logger.debug(f"Parsed options: {self.options}")

    def _parse_options(
        self, options: StirlingPluginAudioOptions | str | dict
    ) -> StirlingPluginAudioOptions | None:
        match self.options:
            case StirlingPluginAudioOptions():
                return options
            case str():
                return StirlingPluginAudioOptions.parse_raw(options)
            case dict():
                b = StirlingPluginAudioOptions.defaults("audio")
                b.update(options)
                print(b)
                exit()
                a = StirlingPluginAudioOptions.parse_obj(options)
                a.merge_default_options(options)
                return StirlingPluginAudioOptions.parse_obj(options)
        self.logger.error(f"Could not parse options for {self.name}")
        raise ValueError(f"Could not parse options for {self.name}")

    def cmds(self, job: StirlingJob):
        """Extract audio from a media file."""
        self._counter += 1
        return [
            StirlingCommand(
                name=f"audio_{str(self._counter)}",
                dependency=job.framework.options.dependencies.get(job.framework.name),
                expected_outputs=[self._cmd_output(job)],
            )
        ]

    def _cmd_output(self, job: StirlingJob):
        return Path(
            job.options.output_directory.resolve()
            / f"audio_{str(self._counter)}.{self.options.container}"
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
