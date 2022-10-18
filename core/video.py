from dataclasses import dataclass, field

import simpleeval

from core import args, definitions, helpers, jobs

required_binaries = ["ffmpeg"]


@dataclass
class StirlingPluginVideo(definitions.StirlingClass):
    """StirlingPluginVideo are arguments for handling the source video
    and our archival encoded copy."""

    _plugin_name: str = "video"

    # Disable creating creating videos or processing any video-dependent
    # plugins. This is not recommended, unless your source is truly audio only.
    video_disable: bool = False
    # In input videos with multiple streams or renditions, specify which one to
    # use. Defaults to the first video stream in the file.
    video_source_stream: int = -1

    # Disable creating individual image frames from the input video.
    video_frames_disable: bool = False
    # The number of frames to capture per second. Can be an integer, a float
    # (decimal), a string that can be parsed to an integer or float, OR it can
    # accept simple mathematical calculations, such as a fraction as a string
    # ("1/10" or "2+"). For more information, see
    # https://github.com/danthedeckie/simpleeval#operators for a list of
    # standard operators. Only operations that return an integer or float
    # (decimal) will return a value. When evaluating mathematical calculations
    # on strings, variables and custom functions are not allowed; this is for
    # security purposes. If no value is provided, or one cannot be calculated
    # from the provided value, then the default is 1 frame per second.
    frames_interval: int = 1

    # The commands we will run to complete this plugin.
    commands: list = field(default_factory=list)
    # Files to output.
    outputs: list = field(default_factory=list)

    def __post_init__(self):
        if not self.video_frames_disable:
            # Check to make sure the appropriate binary files we need are installed.
            assert helpers.check_dependencies_binaries(
                required_binaries
            ), AssertionError("Missing required binaries: {}".format(required_binaries))

    def cmd(self, job: jobs.StirlingJob):
        if (
            self.video_source_stream == -1
            and job.media_info.preferred[self._plugin_name] is not None
        ):
            self.video_source_stream = job.media_info.preferred[self._plugin_name]

        if not self.video_disable:
            if not self.video_frames_disable:
                stream = [
                    item
                    for item in job.media_info.video_streams
                    if item.stream == self.video_source_stream
                ]
                fps = stream[0].frame_rate

                # Set the options to extract audio from the source file.
                options = {
                    "hide_banner": True,
                    "loglevel": "quiet",
                    "y": True,
                    "i": job.media_info.source,
                    "f": "image2",
                    "map": "0:v:{}".format(self.video_source_stream),
                    "vf": "fps={}".format(
                        self.__get_frames_interval(self.frames_interval, fps)
                    ),
                    "vsync": 0,
                    "frame_pts": 1,
                }

                output_directory = job.output_directory / self._plugin_name / "frames"
                output_directory.mkdir(parents=True, exist_ok=True)

                self.commands.append(
                    "ffmpeg {} {}".format(
                        args.default_unparser.unparse(
                            str(job.media_info.source), **options
                        ),
                        str(output_directory) + "%d.jpg",
                    )
                )
                self.outputs.append(output_directory)

    def __get_frames_interval(self, interval, fps):
        # The Frame Interval is the number of frames to capture for every second
        # of video. To capture one frame for every second of video, provide 1 as
        # the value.
        if type(interval) == str:
            try:
                interval = simpleeval.simple_eval(interval)
            # trunk-ignore(flake8/E722)
            except:
                interval = None

        if not isinstance(interval, (int, float, complex)):
            return fps

        return interval
