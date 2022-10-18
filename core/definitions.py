import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import get_type_hints

from dateutil import parser as date_parser

# definitions holds all the standard class definitions and variables we need
# to run jobs.

# StirlingClass is the base class for all Stirling objects. This class adds helper functions that all Stirling objects will use.
class StirlingClass(object):

    # Define a custom function when attempting to set a class attribute
    def __setattr__(self, name, value):
        # Get the type hints from our Job
        proper_type = get_type_hints(self)[name]
        # If necessary, attempt to convert the value to the proper type we
        # expect.
        print("NAME: ", name)
        self.__dict__[name] = type_check(value, proper_type)


# Use this class definition as an example for creating your own StirlingArgsPlugin:
# @dataclass
# class StirlingArgsPlugin(StirlingClass):
#   """You can use this class as a template to
#        create a Argument extend this class and apply your own plugin settings. Just
#        to be sure to create a unique namespace for your plugin, and use it in your
#        variable naming. For example, the hls package generator plugin uses the "hls_"
#        prefix in its argument variable names."""
#    template_argument = Type or default value

# StirlingCmd objects are structures that hold the final command to run for
# a specific step in a job. A StirlingCmd must include the command to run
# in cli style, and the raw output from the command.
@dataclass
class StirlingCmd(StirlingClass):
    """StirlingCmd is the base class for command objects. These command
    objects will be converted into specific commands to run."""

    # The final, completed command that is run.
    command: str = None
    # The output from the command above
    output: str = None


# type_check attempts to set our variable to the proper type.
def type_check(value, proper_type):
    print("VALUE: ", value)
    # If the type of our incoming value and the type we hinted in the
    # object, then let's try to translate it to the proper type.
    a = True
    try:
        a = isinstance(value, proper_type)
    except TypeError:
        # We can't determine the type, so set it as passed.
        value = value
    if not a:
        match proper_type.__name__:
            case "PurePath" | "PurePosixPath" | "PureWindowsPath" | "Path" | "PosixPath" | "WindowsPath":
                if value is None:
                    value = ""
                value = Path(value)
            case "UUID":
                try:
                    value = uuid.UUID(value)
                except ValueError:
                    # We must have a Job ID. If we can't set one, then we'll just create a random one.
                    value = uuid.uuid4()
            case "datetime":
                if type(value) is str and value != "":
                    value = date_parser.parse(value)
            case "float":
                value = float(str(value))
            case "int":
                value = int(float(str(value)))
            case "bool":
                if type(value) is int and (value == 0 or value == 1):
                    value = bool(value)
                elif type(value) is str:
                    match value.lower():
                        case "y" | "yes" | "t" | "true":
                            value = True
                        case "n" | "no" | "f" | "false":
                            value = False
                        case _:
                            # We may want to modify this default case later
                            # to set it to the default or get the value it
                            # already was and leave it as is.
                            value = False
                else:
                    value = False
            case _:
                if value is None:
                    # Allow a None (nil) value
                    pass

    return value


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
