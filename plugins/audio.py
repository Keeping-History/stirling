from dataclasses import dataclass, field
from typing import List

from core import core, job

required_binaries = ["ffmpeg"]


@dataclass
class StirlingPluginAudio(core.StirlingPlugin):
    """StirlingPluginAudio are for using a source audio-only file or for
    extracting audio from a video file. This file is intended as a long-term
    archival version."""

    name: str = "audio"
    depends_on: list = field(default_factory=list)
    priority: int = 100
    # Disables all audio-related tasks. This includes transcripts and peak data
    # generation.
    audio_disable: bool = False
    # In input videos with multiple streams or renditions, specify which one to
    # use. Defaults to the first video stream in the file.
    audio_source_stream: int = -1

    # Additional configuration variables for this plugin.
    # The format to output the audio to, as a tuple. The first value is the
    # encoder format, the file extension is the second value.
    audio_output_format: tuple = ("wav", "wav")

    # Contains outputs from the plugin for use in other plugins.
    assets: List[core.StirlingPluginAssets] = field(default_factory=list)

    ## Extract Audio from file
    def __post_init__(self):
        if not self.audio_disable:
            # Check to make sure the appropriate binary files we need are installed.
            assert core.check_dependencies_binaries(required_binaries), AssertionError(
                "missing required binaries {}".format(required_binaries)
            )

    ## Extract Audio from file
    def cmd(self, job: job.StirlingJob):
        if not self.audio_disable:
            if self.audio_source_stream != -1:
                # If a specific video stream was requested, use that.
                job.media_info.preferred["audio"] = self.video_source_stream

            # Set the options to extract audio from the source file.
            options = {
                "hide_banner": True,
                "y": True,
                "i": job.media_info.source,
                "f": self.audio_output_format[0],
                "map": "0:a:{}".format(
                    job.media_info.preferred["audio"]
                    - len(job.media_info.video_streams)
                ),
            }

            output_directory = job.output_directory / self.name
            output_directory.mkdir(parents=True, exist_ok=True)
            output_file = output_directory / (
                "source.{}".format(self.audio_output_format[1])
            )

            self.assets.append(
                core.StirlingPluginAssets(name="normalized_audio", path=output_file)
            )

            job.commands.append(
                core.StirlingCmd(
                    name=self.name,
                    command="ffmpeg {} {}".format(
                        core.ffmpeg_unparser.unparse(**options), output_file
                    ),
                    priority=self.priority,
                    expected_output=str(output_file),
                    depends_on=self.depends_on,
                )
            )
