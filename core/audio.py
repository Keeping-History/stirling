from dataclasses import dataclass, field
from typing import List

from core import args, definitions, helpers, jobs

required_binaries = ["ffmpeg"]


@dataclass
class StirlingPluginAudio(definitions.StirlingClass):
    """StirlingPluginAudio are for using a source audio-only file or for
    extracting audio from a video file. This file is intended as a long-term
    archival version."""

    _plugin_name: str = "audio"
    _depends_on: list = field(default_factory=list)
    _weight: int = 0
    # Disables all audio-related tasks. This includes transcripts and peak data
    # generation.
    audio_disable: bool = False
    # In input videos with multiple streams or renditions, specify which one to
    # use. Defaults to the first video stream in the file.
    audio_source_stream: int = -1

    # Additional configuration variables for this plugin.
    # The format to output the audio to, as a tuple. The first value is the
    # encoder format, the file extension is the second value.
    audio_output_format: tuple = ("flac", "flac")

    # Command to run to execute this plugin.
    commands: List[definitions.StrilingCmd] = field(default_factory=list)
    # Files to output.
    outputs: list = field(default_factory=list)

    ## Extract Audio from file
    def __post_init__(self):
        if not self.audio_disable:
            # Check to make sure the appropriate binary files we need are installed.
            assert helpers.check_dependencies_binaries(
                required_binaries
            ), AssertionError("missing required binaries {}".format(required_binaries))

    ## Extract Audio from file
    def cmd(self, job: jobs.StirlingJob):
        if (
            self.audio_source_stream == -1
            and job.media_info.preferred[self._plugin_name] is not None
        ):
            self.audio_source_stream = job.media_info.preferred[self._plugin_name]

        # Set the options to extract audio from the source file.
        options = {
            "hide_banner": True,
            "loglevel": "quiet",
            "i": job.media_info.source,
            "f": self.audio_output_format[0],
            "map": "0:a:{}".format(self.audio_source_stream),
        }

        output_directory = job.output_directory / self._plugin_name
        output_directory.mkdir(parents=True, exist_ok=True)
        output_file = output_directory / (
            "source.{}".format(self.audio_output_format[1])
        )

        self.commands.append(
            definitions.StrilingCmd(
                plugin_name=self._plugin_name,
                command="ffmpeg {} {}".format(
                    args.ffmpeg_unparser.unparse(**options), output_file
                ),
                weight=self._weight,
                output=output_file,
                depends_on=self._depends_on,
            )
        )
