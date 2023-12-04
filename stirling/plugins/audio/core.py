from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from stirling.codecs.audio.base import StirlingMediaCodecAudioBase
from stirling.codecs.base import get_codec
from stirling.command.base import StirlingCommand
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


@dataclass(kw_only=True)
class StirlingPluginAudio(StirlingPlugin):
    """StirlingPluginAudio extracts the audio from a source file."""

    name: str = "audio"
    depends_on = None
    options: StirlingPluginAudioOptions | str | dict | None = None
    commands: List[str] = field(default_factory=lambda: ["trim"])

    def __post_init__(self):
        super().__post_init__()
        self._counter: int = 0
        self._cmds = []

        self.options: StirlingPluginAudioOptions = (
            StirlingPluginAudioOptions.parse_options(self.options)
        )
        print(self.options.get_default_options())

        if type(self.options.codec) is str:
            self.options.codec = get_codec(self.options.codec)

        if type(self.options.container) is str:
            self.options.container = get_container(self.options.container)

    def cmds(self, job: StirlingJob):
        """Extract audio from a media file."""
        self._counter += 1
        cmds = []

        for c in self._cmds:
            command, args = list(c.items())[0]
            if "stream" not in args:
                args["stream"] = job.media_info.streams[
                    job.media_info.preferred["audio"]
                ]

            result = ""

            match command:
                case "trim":
                    result = job.framework.trim(
                        args["time_start"],
                        args["time_end"],
                        args["stream"],
                    )
                case "extract":
                    ...
                case "convert":
                    ...
                case _:
                    ...
            print(self.options.codec)
            result += self.options.codec.get()
            cmds.append(
                StirlingCommand(
                    name=f"audio_{self._counter}",
                    dependency=job.framework.get_dependency(),
                    arguments=result,
                    expected_outputs=[self._cmd_output(job)],
                )
            )
        return cmds

    def _cmd_output(self, job: StirlingJob):
        return Path(
            job.options.output_directory.resolve()
            / f"audio_{str(self._counter)}-{self.options.codec.output_name}.{self.options.container.file_extension}"
        )

    def command(self, command: str, arguments: Dict | None = None):
        print("adding command {} with args {}".format(command, arguments))
        if self._validate_command(command):
            self._counter += 1
            self._cmds.append({command: arguments})

    def _validate_command(self, command: str):
        if command not in self.commands:
            raise ValueError(f"Invalid command {command}")
        return True

    # def trim(self, job.json: StirlingJob, stream: StirlingStream):
    #     """Trim audio from a media file."""
    #     self._cmds.append(job.json.framework.trim(1, 2, stream))

    # # Extract Audio from file
    # def cmd(self, job.json: StirlingJob):
    #     if (
    #         self.options.source_stream == -1
    #         and self.name in job.json.media_info.preferred
    #         and job.json.media_info.preferred[self.name] is not None
    #     ):
    #         self.options.source_stream = job.json.media_info.preferred[
    #             self.name
    #         ]
    #
    #     # Set the options to extract audio from the source file.
    #     options = {
    #         "hide_banner": True,
    #         "y": True,
    #         "loglevel": "quiet",
    #         "i": job.json.media_info.source,
    #         "f": self.options.container.file_extension,
    #         "map": "0:a:{}".format(self.options.source_stream),
    #     }
    #
    #     output_directory = job.json.options.output_annotations_directory / self.name
    #     output_directory.mkdir(parents=True, exist_ok=True)
    #     output_file = output_directory / (
    #         "source.{}".format(self.options.container.file_extension)
    #     )
    #
    #     return StirlingCommand(
    #             name=self.name,
    #             dependency=job.json.framework.dependencies.get(job.json.framework.name),
    #             command="ffmpeg {} {}".format(
    #                 args.ffmpeg_unparser.unparse(**options), output_file
    #             ),
    #             priority=self.priority,
    #             expected_output=output_file,
    #             depends_on=self.depends_on,
    #         )
    #     )
