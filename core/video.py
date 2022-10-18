from dataclasses import dataclass, field

import simpleeval

from core import args, definitions, helpers, jobs

required_binaries = ["ffmpeg"]

# EncoderRenditions is a a dict that holds the Video Renditions we support.
# A rendition is a version of the video file that will be transcoded,
# based on the resolution and bitrate settings. The order of these renditions
# is important; the highest-quality rendition should be at the top, followed
# in descending order the remaining lesser-resolution renditions. This is
# because HLS streaming will select the first index.
# These standard profiles should work with any video/audio encoder.
# Quality	    Resolution	bitrate - low	bitrate - high	audio bitrate
# 120p          160x120     96k             128k            32k
# 240p	        426x240	    400k	        600k	        64k
# 360p	        640x360	    700k	        900k	        96k
# 480p	        854x480	    1250k	        1600k	        96k
# 720p	        1280x720	2500k	        3200k	        128k
# 1080p         1920x1080	4500k	        5300k	        128k
# 1080p High  	1920x1080	5800k	        7400k	        192k
# 4k    	    3840x2160	14000k	        18200	        192k
# 4k High   	3840x2160	23000k	        29500k	        192k
# TODO: Finish adding profiles here
EncoderRenditions: dict = {
    "4k-high": {
        "width": "3840",
        "height": "2160",
        "bitrate": "29500",  # KBps
        "audio-bitrate": "192",  # KBps
        "ratio": "16:9",
    },
    "4k": {
        "width": "3840",
        "height": "2160",
        "bitrate": "14000",  # KBps
        "audio-bitrate": "192",  # KBps
        "ratio": "16:9",
    },
    "1080p-high": {
        "name": "1080p-high",
        "width": "1920",
        "height": "1080",
        "bitrate": "7400",  # KBps
        "audio-bitrate": "192",  # KBps
        "ratio": "16:9",
    },
    "1080p": {
        "name": "1080p",
        "width": "1920",
        "height": "1080",
        "bitrate": "7400",  # KBps
        "audio-bitrate": "128",  # KBps
        "ratio": "16:9",
    },
    "720p": {
        "name": "720p",
        "width": "1280",
        "height": "720",
        "bitrate": "7400",  # KBps
        "audio-bitrate": "128",  # KBps
        "ratio": "16:9",
    },
    "480sd": {
        "name": "480p",
        "width": "640",
        "height": "480",
        "bitrate": "800",  # KBps
        "audio-bitrate": "96",  # KBps
        "ratio": "4:3",
    },
    "360sd": {
        "name": "360p",
        "width": "480",
        "height": "360",
        "bitrate": "700",  # KBps
        "audio-bitrate": "96",  # KBps
        "ratio": "4:3",
    },
    "240sd": {
        "name": "240p",
        "width": "320",
        "height": "240",
        "bitrate": "300",  # KBps
        "audio-bitrate": "64",  # KBps
        "ratio": "4:3",
    },
    "120sd": {
        "name": "120p",
        "width": "160",
        "height": "120",
        "bitrate": "128",  # KBps
        "audio-bitrate": "32",  # KBps
        "ratio": "4:3",
    },
}

# EncoderProfiles is a dict that holds the encoder profiles that we support. An
# encoder profile is a collection of renditions for a particular job. When
# creating streaming packages, it's necessary to create multiple renditions of
# an input video. This allows multiple devices, each operating at different
# resolutions and under different network conditions, to choose the video file
# that fits them appropriately. For example, one users might want to access a
# video on be played on a small cell phone in an area with spotty reception,
# while another user may want to play the video on their 4K television with a
# very strong wired internet connection. We call each of these users a "target."
# If we created a single output video, we could create a video that targets one
# or the other, but not both. This would create either an undesirable quality on
# our 4K television or a frustrating loading and buffering experience for our
# cell phone user. By using encoder profiles and modern video streaming encoding
# and formats, we can create a video package that contains a version of the
# video, encoded for multiple targets. Using this, the video player can make its
# own determinations about network availability and quality tradeoffs. This is
# also helpful for our 4K TV target, as no network connection is ever stable. In
# the event of a network slowdown, the 4K TV's video player can decide to revert
# to a lower quality with a smaller bitrate, therefore keeping the video playing
# and limiting buffering and pausing. In each of our EncoderProfiles, we specify
# a list of targets that we want to encode. The Stirling Engine, when encoding a
# streaming video package (such as HLS or DASH), it will create a separate video
# encoding job for each rendition. When each rendition is done, they will be
# merged into one package. The video player only needs the url to our finished
# package, and it will decide which video stream to use.
EncoderProfiles: dict = {
    "sd": [
        EncoderRenditions["120sd"],
        EncoderRenditions["240sd"],
        EncoderRenditions["480sd"],
    ],
    "hd": [
        EncoderRenditions["720p"],
        EncoderRenditions["1080p"],
        EncoderRenditions["1080p-high"],
    ],
}

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
            assert helpers.check_dependencies_binaries(required_binaries), AssertionError("Missing required binaries: {}".format(required_binaries))

    def cmd(self, job: jobs.StirlingJob):
        if self.video_source_stream == -1 and job.media_info.preferred[self._plugin_name] is not None:
            self.video_source_stream = job.media_info.preferred[self._plugin_name]

        if not self.video_disable:
            if not self.video_frames_disable:
                stream = [item for item in job.media_info.video_streams if item.stream==self.video_source_stream]
                fps = stream[0].frame_rate

                # Set the options to extract audio from the source file.
                options = {
                    'hide_banner': True,
                    'loglevel': "quiet",
                    'y': True,
                    'i': job.media_info.source,
                    'f': "image2",
                    'map':"0:v:{}".format(self.video_source_stream),
                    'vf':"fps={}".format(self.__get_frames_interval(self.frames_interval, fps)),
                    'vsync': 0,
                    'frame_pts': 1,
                }

                output_directory = job.output_directory / self._plugin_name / "frames"
                output_directory.mkdir(parents=True, exist_ok=True)

                self.commands.append("ffmpeg {} {}".format(args.default_unparser.unparse(str(job.media_info.source), **options), str(output_directory) + "%d.jpg"))
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
