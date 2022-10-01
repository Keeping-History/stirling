import datetime
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, get_type_hints

from core import helpers

# definitions holds all the standard class definitions and variables we need
# to run jobs.


class StirlingClass(object):
    # The base class for all Stirling objects. This class adds helper
    # functions that all Stirling objects will use.

    # Define a custom function when attempting to set a class attribute
    def __setattr__(self, name, value):
        # Get the type hints from our Job
        proper_type = get_type_hints(self)[name]
        # If necessary, attempt to convert the value to the proper type we
        # expect.
        self.__dict__[name] = helpers.type_check(value, proper_type)


@dataclass
class StirlingOutputs(StirlingClass):
    """StirlingOutputs is a collection for all the files output for a job."""

    # The output directory for the package and its contents
    directory: Path = None
    # Specific output files/directories generated are put here
    outputs: List[dict] = field(default_factory=list)


@dataclass
class StirlingJob(StirlingClass):
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
    output: StirlingOutputs = None


# StirlingArgs Types
# These StirlingArgs types include all of the arguments available to pass in to the
# Stirling Engine (excluding any custom plugins). During startup, all StirlingArgs
# Types will be merged into one. It is very important to note that only
# arguments specified by the Stirling Engine and its Core Plugins can provide
# any arguments that are not prefixed with the namespace of the plugin, followed
# by an underscore ("_"). All Argument objects will be merged into one. In case
# of an argument conflict, the order the arguments are merged in will determine
# which argument, in the end, is used. First, any custom StirlingArgsPluginX types
# will be merged together; it's important to note there is no guarantee a
# particular plugin will be able to set a shared argument name, so it's
# important to use name prefixes. Next, the StirlingArgsPluginDefault values are
# merged. Next, the StirlingArgsCore object is merged. Finally, the StirlingArgsJob
# will be merged. In case of an argument conflict, the latest merged object,
# from the order above, will win and be set.


@dataclass
class StirlingArgsJob(StirlingClass):
    """StirlingArgsJob are base arguments necessary to start up the Stirling job
    runner. These includes things like input and output file and directories,
    and other options related to the running of the job."""

    # The Job File, a JSON document that describes the whole job. If it is
    # available, then we will apply it over these defaults.
    job_file: Path = None
    # The input source filename
    source: Path = None
    # In input videos with multiple streams or renditions, specify which one to
    # use. Defaults to the first video stream in the file.
    source_video_stream: int = -1
    # In input videos with multiple streams or renditions, specify which one to
    # use. Defaults to the first video stream in the file.
    source_audio_stream: int = -1
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
        # The input source file is required.
        if name == "source" and name is None:
            raise ValueError
        return super().__setattr__(name, value)


@dataclass
class StirlingArgsCore(StirlingClass):
    """StirlingArgsCore are parameters passed to the Core Plugins. Core Plugins are
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
