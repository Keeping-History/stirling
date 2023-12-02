from dataclasses import dataclass
from pathlib import Path

from stirling.codecs.audio.base import StirlingMediaCodecAudioBase
from stirling.codecs.base import get_codec
from stirling.command.base import StirlingCommand
from stirling.containers.base import StirlingMediaContainer, get_container
from stirling.frameworks.base import StirlingStream
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
        self._commands = []

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

        return self._commands

    def _cmd_output(self, job: StirlingJob):
        return Path(
            job.options.output_directory.resolve()
            / f"audio_{str(self._counter)}-{self.options.codec.output_name}.{self.options.container.file_extension}"
        )

    def _add_command(self, command: StirlingCommand):
        self._counter += 1
        self._commands.append(
                command
        )

    def trim(self, job: StirlingJob, stream: StirlingStream):
        """Trim audio from a media file."""

        # print(my_job.framework.trim(1, 2, my_job.media_info.get_preferred_stream("audio")))

        self._add_command(
                StirlingCommand(
                    name=f"audio_{self._counter}",
                    dependency=job.framework.get_dependency(),
                    expected_outputs=[self._cmd_output(job)],
                )
        )

    # # Extract Audio from file
    # def cmd(self, job: StirlingJob):
    #     if (
    #         self.options.source_stream == -1
    #         and self.name in job.media_info.preferred
    #         and job.media_info.preferred[self.name] is not None
    #     ):
    #         self.options.source_stream = job.media_info.preferred[
    #             self.name
    #         ]
    #
    #     # Set the options to extract audio from the source file.
    #     options = {
    #         "hide_banner": True,
    #         "y": True,
    #         "loglevel": "quiet",
    #         "i": job.media_info.source,
    #         "f": self.options.container.file_extension,
    #         "map": "0:a:{}".format(self.options.source_stream),
    #     }
    #
    #     output_directory = job.options.output_annotations_directory / self.name
    #     output_directory.mkdir(parents=True, exist_ok=True)
    #     output_file = output_directory / (
    #         "source.{}".format(self.options.container.file_extension)
    #     )
    #
    #     return StirlingCommand(
    #             name=self.name,
    #             dependency=job.framework.dependencies.get(job.framework.name),
    #             command="ffmpeg {} {}".format(
    #                 args.ffmpeg_unparser.unparse(**options), output_file
    #             ),
    #             priority=self.priority,
    #             expected_output=output_file,
    #             depends_on=self.depends_on,
    #         )
    #     )
