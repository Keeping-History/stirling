from calendar import c
import uuid
import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, OrderedDict, get_type_hints
import collections
import pathlib
from dateutil import parser as date_parser

# definitions holds all the standard class definitions and variables we need
# to run jobs.

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
EncoderRenditions:OrderedDict = {
    "4k-high": {
        "width": "3840",
        "height": "2160",
        "bitrate": "29500",  # KBps
        "audio-bitrate": "192",  # KBps
        "ratio": "16:9"
    },
    "4k": {
        "width": "3840",
        "height": "2160",
        "bitrate": "14000",  # KBps
        "audio-bitrate": "192",  # KBps
        "ratio": "16:9"
    },
    "1080p-high": {
        "name": "1080p-high",
        "width": "1920",
        "height": "1080",
        "bitrate": "7400",  # KBps
        "audio-bitrate": "192",  # KBps
        "ratio": "16:9"
    },
    "1080p": {
        "name": "1080p",
        "width": "1920",
        "height": "1080",
        "bitrate": "7400",  # KBps
        "audio-bitrate": "128",  # KBps
        "ratio": "16:9"
    },
    "720p": {
        "name": "720p",
        "width": "1280",
        "height": "720",
        "bitrate": "7400",  # KBps
        "audio-bitrate": "128",  # KBps
        "ratio": "16:9"
    },
    "480sd": {
        "name": "480p",
        "width": "640",
        "height": "480",
        "bitrate": "800",  # KBps
        "audio-bitrate": "96",  # KBps
        "ratio": "4:3"
    },
    "360sd": {
        "name": "360p",
        "width": "480",
        "height": "360",
        "bitrate": "700",  # KBps
        "audio-bitrate": "96",  # KBps
        "ratio": "4:3"
    },
    "240sd": {
        "name": "240p",
        "width": "320",
        "height": "240",
        "bitrate": "300",  # KBps
        "audio-bitrate": "64",  # KBps
        "ratio": "4:3"
    },
    "120sd": {
        "name": "120p",
        "width": "160",
        "height": "120",
        "bitrate": "128",  # KBps
        "audio-bitrate": "32",  # KBps
        "ratio": "4:3"
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
EncoderProfiles: collections.OrderedDict = ({
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
})

@dataclass
class Job:
    "A Stirling Engine Job definition"

    # id is the ID of the job. We create a random UUID whenever a job is
    # created, however a custom one can be supplied so long as it is assured to
    # be globally unique (or at least try your best).
    id: uuid.UUID = uuid.uuid4()
    # time_start is the start time of the job, as a datetime.datetime object in
    # UTC.
    time_start: datetime.datetime = datetime.datetime.now()
    # time_end is the end time of the job, as a datetime.datetime object in UTC.
    time_end: datetime.datetime = None
    # duration is the length of the job run time, in seconds.
    duration: float = 0.0
    # log_file is the filename of the job log file.
    log_file: Path = Path("./job.log")
    # job_file is the filename of the JSON job file to save.
    job_file: Path = Path("./job.json")
    # arguments is a holder for job arguments we'll use later.
    arguments: dict = field(default_factory=dict)

    def __setattr__(self, name, value):
        # Get the type hints from our Job
        proper_type = get_type_hints(Job)[name]
        print(
            "Name       :", name,
            "\nProper Type: ", type(proper_type),
            "\nIn Value   : ",value,
            "\nIn Type    :", type(value),
            "\n"
        )

        # If the type of our incoming value and the type we hinted in the
        # object, then let's try to translate it to the proper type.
        if not isinstance(value, proper_type):
            match proper_type:
                case pathlib.Path:
                    if value is None:
                        value = ""
                    value = pathlib.Path(value)
                case uuid.UUID:
                    try:
                        value = uuid.UUID(value)
                    except ValueError:
                        value = uuid.uuid4()
                case datetime.datetime:
                    if type(value) is str:
                        value = date_parser.parse(value)
                case float() as proper_type:
                    if type(value) is str or type(value) is int:
                        value = float(str(value))
                case _:
                    if value is None:
                        pass
                    raise ValueError

        self.__dict__[name] = value


# Arguments Types
# These Arguments types include all of the arguments available to pass in to the
# Stirling Engine (excluding any custom plugins). During startup, all Arguments
# Types will be merged into one. It is very important to note that only
# arguments specified by the Stirling Engine and its Core Plugins can provide
# any arguments that are not prefixed with the namespace of the plugin, followed
# by an underscore ("_"). All Argument objects will be merged into one. In case
# of an argument conflict, the order the arguments are merged in will determine
# which argument, in the end, is used. First, any custom ArgumentsPlugin types
# will be merged together; it's important to note there is no guarantee a
# particular plugin will be able to set a shared argument name, so it's
# important to use name prefixes. Next, the ArgumentsPluginDefault values are
# merged. Next, the ArgumentsCore object is merged. Finally, the ArgumentsCLI
# will be merged. In case of an argument conflict, the latest merged object,
# from the order above, will win and be set.

@dataclass
class ArgumentsJob:
    """ArgumentsJob are base arguments necessary to start up the Stirling job
    runner. These includes things like input and output file and directories,
    and other options related to the running of the job."""

    # The Job File, a JSON document that describes the whole job. If it is
    # available, then we will apply it over these defaults.
    job_file: Path = None
    # The input source filename
    source: Path = None
    # The directory to output the package. Defaults to a folder named with the
    # job's ID (a random UUID) in the current working folder.
    output: Path = None
    # The folder prefix where incoming files are located. Defaults to the
    # current working directory.
    input_directory: Path = None
    # Add a prefix to the output directory automatically. Defaults to "output".
    output_directory_prefix: str = "output"
    # Delete the temporary incoming source file when finished. By default, the
    # temporary incoming source file is deleted.
    disable_delete_source: bool = True
    # When a job is completed, a copy of the video file as it was uploaded is
    # created in the output directory as "source". This can be disabled.
    disable_source_copy: bool = True
    # A debugging option that attempts to setup a full job without actually
    # doing any of the external transcoding/extraction. This should be removed.
    simulate: bool = False
    # Enable additional debugging output.
    debug: bool = True

    def __setattr__(self, name, value):
        match name:
            case 'job_file' | 'source' | 'output' | 'input_directory':
                if value is None:
                    value = ""
                value = pathlib.Path(value)

        self.__dict__[name] = value

@dataclass
class ArgumentsCore:
    """CoreArguments are parameters passed to the Core Plugins. Core Plugins are
    essentially a set of utilities that are necessary for the Stirling Engine to
    function. Core Plugins also provide the bare input for all of the Stirling
    Engine default provided plugins, as well as any custom plugins. Some examples
    of of these Core Plugin functions include extracting audio from video,
    extracting image frames from a video file, as well as creating a normalized
    video from the input file, all of which can be provided to plugins later on in
    the job."""

    # Disables all audio-related tasks. This includes transcripts and peak data
    # generation.
    disable_audio: bool = False
    # Disable creating individual image frames from the input video.
    disable_frames: bool = False
    # In input videos with multiple streams or renditions, specify which one to
    # use. Defaults to the first video stream in the file.
    input_video_stream: int = -1
    # In input videos with multiple streams or renditions, specify which one to
    # use. Defaults to the first video stream in the file.
    input_audio_stream: int = -1

@dataclass
class ArgumentsPluginFrames:
    """ArgumentsPluginFrames are for extracting image frames from the source
    video. This is helpful for later machine learning processing or for
    scrub/thumbnail images."""

    # The number of frames to capture per second. Can be an integer, a float
    # (decimal), a string that can be parsed to an integer or float, OR it can
    # accept simple mathematical calculations, such as a fraction as a string
    # ("1/10" or "2+"). For more information, see
    # https://github.com/danthedeckie/simpleeval#operators for a list of
    # standard operators. Only operations that return an integer or float
    # (decimal) will return a value.  When evaluating mathematical calculations
    # on strings, variables and custom functions are not allowed; this is for
    # security purposes. If no value is provided, or one cannot be calculated
    # from the provided value, then the default is 1 frame per second.
    frames_interval: int = 1

@dataclass
class ArgumentsPluginTranscript:
    """ArgumentsPluginTranscript are for creating speech-to-text transcripts.
    These transcripts can be used as-is, or can be used later for
    confidence training, language analysis or for adding other contexts."""

    # Disable the transcript extraction.
    transcript_disable: bool = False

@dataclass
class ArgumentsPluginPeaks:
    """ArgumentsPluginPeaks are are for creating waveform peaks from the input
    source's audio track."""

    # Disable the generation of audio peak data.
    peaks_disable: bool = False

@dataclass
class ArgumentsPluginHLS:
    """ArgumentsPluginHLS are for creating an HLS VOD streaming package from
    the input source video."""

    # Disable creating an HLS VOD package.
    hls_disable: bool = False
    # The encoding profile to use. Defaults to "sd".
    hls_profile: str = "sd"
    # The length of each segmented file.
    hls_segment_duration: int = 4
    # The bitrate ratio to use when determining the maximum bitrate for the
    # video.
    hls_bitrate_ratio: int = 1.07
    # The ratio to use when determining the optimum buffer size.
    hls_buffer_ratio: int = 1.5
    # The Constant Rate Factor to use when encoding HLS video. Lower numbers are
    # better quality, but larger files. Defaults to 20. Recommended values are
    # 18-27.
    hls_crf: int = 20
    # The keyframe multiplier. The current framerate is multiplied by this
    # number to determine the number the maximum length before the encoder
    # creates a new one. Defaults to 1.
    hls_keyframe_multiplier: int = 1


# Use this class definition as an example for creating your own ArgumentsPlugin:
# @dataclass
# class ArgumentsPluginTemplate:
#   """You can use this class as a template to
#        create a Argument extend this class and apply your own plugin settings. Just
#        to be sure to create a unique namespace for your plugin, and use it in your
#        variable naming. For example, the hls package generator plugin uses the "hls_"
#        prefix in its argument variable names."""
#    template_argument = Type or default value

@dataclass
class Output:
    """Outputs is a collection for all the files output for a job."""
    # The output directory for the package and its contents
    directory: Path = None
    # Specific output files/directories generated are put here
    outputs: List[dict] = field(default_factory=list)

    def __setattr__(self, name, value):
        match name:
            case 'directory':
                if value is None:
                    value = ""
                value = pathlib.Path(value)

        self.__dict__[name] = value

@dataclass
class CommandBase:
    # The final, completed command that is run.
    command: str = None
    # The output from the command above
    output: str = None

@dataclass
class CommandHLS(CommandBase):
    """CommandHLS contains a mapping of our input arguments to the necessary
        CLI arguments that our video transcoder will need. Currently, we
        use ffmpeg, but others could be used by mapping the proper input
        parameters to the command parameters our transcoder requires."""

    args = collections.OrderedDict({
        "hls_profile": "sd",
        "hls_bitrate_ratio": 1,
        "hls_buffer_ratio": 1,
    })

    # A set of input options for the encoder.
    input_options = collections.OrderedDict(
        {
            # The source (input) file
            "i": None,
            # The stream to use for the input. For more information
            # se https://trac.ffmpeg.org/wiki/Map
            "map": None,
        }
    ),

    output_options = collections.OrderedDict(
        {
            # The output directory for the HLS package.
            "directory": None,
        }
    ),
    cli_options = collections.OrderedDict(
        {
            # Hide ffmpeg"s console banner output.
            "hide_banner": True,
            # Tell ffmpeg to just agree to whatever
            "y": True,
            # Output log level. See here for more on loglevels:
            # https://ffmpeg.org/ffmpeg.html#Generic-options
            "loglevel": "debug",
        }
    ),
    options = collections.OrderedDict(
        {
            # Audio codec to encode with. We prefer AAC over mp3.
            "acodec": "aac",
            # Audio sample rate to encode with. Default is the same as the source.
            "ar": "44100",
            # Video codec to encode with. H264 is the most common and our preferred codec for compatibility purposes.
            "vcodec": "h264",
            # Video encoding profile, set to a legacy setting for compatibility.
            "profile:v": "main",
            # The CRF value to use when encoding HLS video, lower is better
            # quality. A "sane" value is 17-28. Default is 20. Currently, we are using
            # args for this, but it is here to represent the template for future use.
            "crf": "20",
            # Adjusts the sensitivity of x264's scenecut detection. Rarely needs to be adjusted. 0 disables scene detection. Recommended default: 40
            "sc_threshold": "40",
            # Set the Group Picture Size (GOP). Default is 12.
            "g": "12",
            # Set the minimum distance between keyframes.
            "keyint_min": "25",
            # The target length of each segmented file. Default is 2.
            "hls_time": "2",
            # The type of HLS playlist to create.
            "hls_playlist_type": "vod",
            # Enable faster file streaming start for HLS files by moving some of the metadata to the beginning of the file after transcode.
            "movflags": "+faststart",
            # Audio codec to encode with. We prefer AAC over mp3.
            # Scale the video to the appropriate resolution.
            "vf": "",
            "b:v": "",
            # Set the maximum video bitrate.
            "maxrate": "",
            # Set the size of the buffer before ffmpeg recalculates the bitrate.
            "bufsize": "",
            # Set the audio output bitrate.
            "b:a": "",
        }
    ),
    rendition_options =  collections.OrderedDict(
        {
            # Scale the video to the appropriate resolution. A default string template is provided to input the width and height.
            "vf": "scale=w={}:h={}:force_original_aspect_ratio=decrease",
            # Control the bitrate. A default string template is provided.
            "b:v": "{}k",
            # Set the maximum video bitrate. A default string template is provided.
            "maxrate": "{0}k",
            # Set the size of the buffer before ffmpeg recalculates the bitrate. A default string template is provided.
            "bufsize": "{0}k",
            # Set the audio output bitrate. A default string template is provided.
            "b:a": "{0}k",
            # Set the output filename for the HLS segment. A default string template is provided.
            "hls_segment_filename": "{0}/{1}_%09d.ts' '{0}/{1}.m3u8",
        }
    ),
    encoder_profiles = EncoderProfiles,
