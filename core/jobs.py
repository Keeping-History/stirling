import json
import os
import shutil
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, urlsplit

import requests
import validators
from mergedeep import merge

from core import definitions, probe, strings


@dataclass
class StirlingJob(definitions.StirlingClass):
    """A Stirling Engine Job definition are the base arguments and information
    necessary to start up the Stirling job runner. These includes things like
    input and output file and directories, and other options related to the
    running of the job."""

    ### Required Variables
    # The input source filename
    source: str
    ### Job-specific variables
    # id is the ID of the job. We create a random UUID whenever a job is
    # created, however a custom one can be supplied so long as it is assured to
    # be globally unique (or at least try your best).
    id: uuid.UUID = uuid.uuid4()
    # time_start is the start time of the job, as a datetime.datetime object in
    # UTC.
    time_start: datetime = datetime.now()
    # time_end is the end time of the job, as a datetime.datetime object in UTC.
    time_end: datetime = None
    # duration is the length of the job run time, in seconds.
    duration: float = 0.0
    # log_file is the filename of the job log file.
    log_file: Path = Path("./job.log")
    # job_file is the filename of the JSON job file to save.
    job_file: Path = Path("./job.json")

    ### Source input variables
    # The folder prefix where incoming files are located. Defaults to the
    # current working directory.
    input_directory: Path = Path(os.getcwd())
    # Delete the temporary incoming source file when finished. By default, the
    # temporary incoming source file is deleted.
    source_delete_disable: bool = True

    ### Output variables
    # The directory to output the package. Defaults to a folder named with the
    # job's ID (a random UUID) in the current working folder.
    output_directory: Path = Path(os.getcwd())
    # The directory to store annotations in. Defaults to a folder named annotations.
    output_annotations_directory: str = "annotations"
    # When a job is completed, a copy of the video file as it was uploaded is
    # created in the output directory as "source". This can be disabled.
    source_copy_disable: bool = True

    ### Others
    # A debugging option that attempts to setup a full job without actually
    # doing any of the external transcoding/extraction. This should be removed.
    simulate: bool = False
    # Enable additional debugging output.
    debug: bool = True

    ### Variable Holders
    # media_info contains source information after being probed.
    media_info: probe.SterlingMediaInfo = None
    # plugins is a holder for plugin arguments we'll use later.
    plugins: list = field(default_factory=list)
    # Specific output files/directories generated are put here
    outputs: list = None

    def open(self):
        # Check to see if a Job JSON file was passed and parse it
        # TODO: see self.load()
        # if self.job_file.is_file():
        #    self.load()

        # Setup our output directory
        self.__get_output_directory()
        # Validate our incoming source file
        self.__get_source()

        # Logging
        self.log("Starting job")
        self.log("Job Definition: ", self)
        self.log("Output Directory will be: " + str(self.output_directory))
        self.log("File to processed will be: " + str(self.source))

        # Probe the source file
        self.media_info = probe.SterlingMediaInfo(source=self.source)
        self.log("Media file {} probed: ".format(self.source), self.media_info)

    def load(self):
        # TODO: Implement the actual merge from a JSON job file
        #  This whole function is just a
        #  placeholder stub
        with open(self.job_file) as json_file:
            # Load the file into our Job Object
            new_job = json.load(json_file)
            job = merge({}, self, new_job)
            self.log("Loaded job: ", job)

    def close(self):
        # Close out the job and update its metadata
        self.time_end = datetime.now()
        self.duration = (self.time_end - self.time_start).total_seconds()
        self.log(
            "Ending job {} at {}, total duration: {}".format(
                self.id, self.time_end, self.duration
            ),
        )
        self.write()

    def write(self):
        # Write the object to a file
        output_file = open(self.job_file, "w")
        output_file.write(json.dumps(self, indent=4, cls=strings.JobEncoder))
        output_file.close()

    def log(self, message, *args):
        stamp = datetime.now()
        obj_log = ""
        duration = str((stamp - self.time_start))
        line_header = "[{}] [+{}] [{}]".format(
            stamp.strftime("%Y-%m-%d %H:%M:%S"), duration, self.id
        )

        for object_to_log in args:
            obj_log += self.__log_object(object_to_log)

        if self.debug:
            print("{}: {}{}".format(line_header, message, obj_log))

        try:
            file1 = open(self.log_file, "a")  # append mode
            file1.write("{}: {}".format(line_header, message))

            # If we have any objects to log, log them
            for line in obj_log.split("\n"):
                # We're looping here in case we want to prettify each line
                # (like above) in the future.
                file1.write(line + "\n")

            file1.close()

        except OSError:
            raise Exception(
                "can't access the log file: {}, stopping execution for job {}".format(
                    self.log_file, str(self.id)
                )
            )

    def __log_object(
        self, obj, line_identifier: str = "+", header: str = "", indent: int = 4
    ):
        return self.__log_string(
            header + json.dumps(vars(obj), indent=indent, cls=strings.JobEncoder),
            line_identifier,
            indent,
        )

    def __get_source(self):

        # If the incoming source is a URL, then let's download it.
        if validators.url(self.source, public=False):
            response = requests.get(self.source)
            incoming_filename = "".join(
                os.path.splitext(os.path.basename(urlsplit(self.source).path))
            )
            self.source = incoming_filename
            if response.ok:
                open(incoming_filename, "wb").write(response.content)
            else:
                raise FileNotFoundError(
                    "Unable to download source file from URL: {}".format(self.source)
                )

        # Get a full path to name our source file when we move it. We'll use this
        # value later on as an input filename for specific commands.
        incoming_filename = (
            str(self.output_directory) + "/source" + Path(self.source).suffix
        )

        if not self.source_copy_disable:
            # Unless this is a simulation or we explicitly disabled it, copy the source
            # file to the output directory as 'source'
            shutil.copyfile(Path(self.source).absolute(), incoming_filename)
            if not self.source_delete_disable:
                # Don't delete the incoming source file, in case we're testing.
                os.remove(self.source)

        self.source = Path(incoming_filename)

    def __get_output_directory(self):
        # Make the output directory, if it doesn't exist.
        if not self.output_directory.is_dir():
            self.output_directory.mkdir(parents=True, exist_ok=True)
            annotations_output_directory = (
                self.output_directory / self.output_annotations_directory
            )
            annotations_output_directory.mkdir(parents=True, exist_ok=True)

        self.log_file = self.output_directory / self.log_file
        self.job_file = self.output_directory / self.job_file

        # Make sure we have a directory for the output files
        assert self.output_directory.is_dir(), self.log(
            "could not find the path {} for output files".format(
                str(self.output_directory)
            ),
        )

        # Make sure we can write to the directory for the output files
        assert os.access(self.output_directory, os.W_OK), self.log(
            "could not write to path {} for output files".format(
                str(self.output_directory)
            )
        )

    def __log_string(self, string, line_identifier="+", indent=4):
        new_line_string = "\n" + line_identifier + " " * indent
        return new_line_string + new_line_string.join(string.splitlines())

    def __is_url(self):
        try:
            result = urlparse.urlparse(self.source)
            print(result)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False


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
# important to use name prefixes. Next, the StirlingArgsJob
# will be merged. In case of an argument conflict, the latest merged object,
# from the order above, will win and be set.
