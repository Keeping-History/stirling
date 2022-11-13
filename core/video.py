from dataclasses import dataclass, field
from typing import List

from core import args, definitions, helpers, jobs, encoders

required_binaries = ["ffmpeg"]

@dataclass
class StirlingPluginVideo(definitions.StirlingPlugin):
    """StirlingPluginVideo are arguments for handling the source video
    and our archival encoded copy."""

    name: str = "video"
    depends_on: list = field(default_factory=list)
    priority: int = 0

    # Disable creating creating videos or processing any video-dependent
    # plugins. This is not recommended, unless your source is truly audio only.
    video_disable: bool = False
    # In input videos with multiple streams or renditions, specify which one to
    # use. Defaults to the first video stream in the file.
    video_source_stream: int = -1

    # The interval to insert keyframes. This is multipled by the frame rate to
    # achieve the keyframe interval in seconds. To achieve a keyframe every 2
    # seconds, set this to 2. To achieve a keyframe every 3 seconds for a 30fps
    # video, set this to 0.1.
    video_keyframe_interval: float = 1.0

    video_container_format: str = "mp4"
    video_codec_format: str = "h264"
    video_streaming_optimize: bool = False
    video_rtp_hints: bool = False
    video_copy_all_streams: bool = False
    video_encoder_options: dict = field(default_factory=dict)

    # Contains outputs from the plugin for use in other plugins.
    assets: List[definitions.StirlingPluginAssets] = field(default_factory=list)

    def __post_init__(self):
        if not self.video_disable:
            # Check to make sure the appropriate binary files we need are installed.
            assert helpers.check_dependencies_binaries(
                required_binaries
            ), AssertionError("Missing required binaries: {}".format(required_binaries))

    def get_encoder(self, job: jobs.StirlingJob, format: str, encoder: str):
        match format:
            case "av1":
                stream = job.media_info.get_preferred_stream("video")
                keyframe_interval = stream.frame_rate * self.video_keyframe_interval
                self.video_encoder_options = encoders.StirlingVideoEncoderAV1().get_encoder_options("aom")
                self.video_encoder_options["g"] = self.video_encoder_options["keyint_min"] = keyframe_interval
                return definitions.EncoderOptionsAV1

    def cmd(self, job: jobs.StirlingJob):
        if not self.video_disable:
            if self.video_source_stream != -1:
                # If a specific video stream was requested, use that.
                job.media_info.preferred["video"] = self.video_source_stream

            # Set the options to extract audio from the source file.
            options = {
                "hide_banner": True,
                "y": True,
                "i": job.media_info.source,
                "map": "0:v:{}".format(job.media_info.preferred["video"]),
            } | self.get_encoder("av1")

            output_directory = job.output_directory / self.name
            output_directory.mkdir(parents=True, exist_ok=True)

            self.assets.append(
                definitions.StirlingPluginAssets(name="video_archive", path=output_directory)
            )

            job.commands.append(
                definitions.StirlingCmd(
                    name=self.name,
                    depends_on=self.depends_on,
                    command="ffmpeg {} {}".format(
                        args.ffmpeg_unparser.unparse(
                            **options
                        ),
                        "source.mp4",
                    ),
                    priority=0,
                    expected_output=str(output_directory),
                )
            )
