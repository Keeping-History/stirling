import json
import os
import shutil
import subprocess
import textwrap
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List
from urllib.parse import urlparse, urlsplit

import networkx
import requests
import validators

from core import definitions, helpers, probe

# TODO: Need this later for merging in a json job file.
# from mergedeep import merge


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
    output_directory: Path = None
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
    media_info: probe.StirlingMediaInfo = None
    # plugins is a holder for plugin arguments we'll use later.
    plugins: List = field(default_factory=list)
    # Specific output files/directories generated are put here
    _outputs: List = field(default_factory=list)
    # Commands to fire off
    commands: List[definitions.StrilingCmd] = field(default_factory=list)

    def __post_init__(self):
        if self.job_file.is_file():
            self.load()

        # Setup our output directory
        self.__get_output_directory()

        # Logging
        self.log("Starting job")
        self.log("Job Definition: ", self)
        self.log("Output Directory will be: " + str(self.output_directory))

        # Validate our incoming source file
        self.__get_source()

        # Probe the source file
        self.media_info = probe.StirlingMediaInfo(source=self.source)
        self.log("Media file {} probed: ".format(self.source), self.media_info)
        self.write()

    def add_plugins(self, *args):
        for plugin in args:
            self.plugins.append(plugin)
            self.log('Added plugin "{}". '.format(plugin.plugin_name))
        self.__parse()
        self.write()

    def load(self):
        # TODO: Implement the actual merge from a JSON job file
        #  This whole function is just a
        #  placeholder stub
        # with open(self.job_file) as json_file:
        #     # Load the file into our Job Object
        #     new_job = json.load(json_file)
        #     job = merge({}, self, new_job)
        #     self.log("Loaded job: ", job)
        pass

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

    def run(self):
        cmd_holder = []
        for cmd in self.commands:
            # Check if we can probe the input file.
            cmd.status = definitions.StirlingCmdStatus.RUNNING
            self.log(
                "Starting command {} for plugin {}".format(
                    textwrap.shorten(cmd.command, width=20), cmd.plugin_name
                )
            )
            cmd_output = subprocess.getstatusoutput(cmd.command)
            cmd.log = cmd_output[1]
            if cmd_output[0] != 0:
                cmd.status = definitions.StirlingCmdStatus.FAILED
                self.log(
                    "Command {} for plugin {} failed.".format(
                        textwrap.shorten(cmd.command, width=20), cmd.plugin_name
                    )
                )
                self.log("Command for plugin {}:".format(cmd.plugin_name), cmd.command)
                self.log("Output:", cmd.log)
            elif cmd_output[0] == 1:
                self.log(
                    "Command {} for plugin {} succeeded.".format(
                        textwrap.shorten(cmd.command, width=20), cmd.plugin_name
                    )
                )
                cmd.status = definitions.StirlingCmdStatus.SUCCESS

                self.log(
                    "Command {} for plugin {} output:".format(
                        textwrap.shorten(cmd.command, width=20), cmd.plugin_name
                    ),
                    cmd.log,
                )
            self.write()

            cmd_holder.append(cmd)

        self.commands = cmd_holder

    def __parse(self):
        # Clear the commands list, as we will re-parse them all
        self._outputs = []

        # Create some holder variables
        cmd_sort_holder = {}
        cmd_output_holder = []

        for plugin in self.plugins:
            self.log('Parsing plugin "{}" commands.'.format(plugin.plugin_name))
            plugin.cmd(self)

            # Sort each command in the plugin by its priority/priority
            self.commands.sort(key=lambda x: x.priority, reverse=True)

            # Create a holder so we can run a topographical sort on the commands
            for cmd in self.commands:
                if len(cmd.depends_on) > 0:
                    cmd_sort_holder[cmd.plugin_name] = cmd.depends_on

        if len(cmd_sort_holder) > 1:
            self.log(
                'Parsing plugin "{}" dependencies {}.'.format(
                    plugin.plugin_name, plugin.depends_on
                )
            )

            # Sort the commands by their dependencies
            cmd_sort_list = list(
                reversed(
                    list(networkx.topological_sort(networkx.DiGraph(cmd_sort_holder)))
                )
            )

            # Reorder the commands based on the topographical sort
            for v in cmd_sort_list:
                for cmd in self.commands:
                    if cmd.plugin_name == v:
                        self.log(
                            'Appending command for plugin "{}": {}.'.format(
                                cmd.plugin_name, cmd.command
                            )
                        )
                        cmd_output_holder.append(cmd)
                        self._outputs.append(str(cmd.expected_output))

        # Create the necessary folders for the plugin outputs
        for output in self._outputs:
            output_dir = Path(os.path.dirname(Path(output)))
            output_dir.mkdir(parents=True, exist_ok=True)

        # Set the commands to the sorted list
        self.commands = cmd_output_holder
        self.log("Plugins added {} commands.".format(len(self.commands)))

    def write(self):
        # Write the object to a file
        output_file = open(self.job_file, "w")
        output_file.write(json.dumps(self, indent=4, cls=helpers.StirlingJSONEncoder))
        output_file.close()

    def log(self, message: str, *args):
        stamp = datetime.now()
        obj_log = ""
        duration = str((stamp - self.time_start))
        line_header = "[{}] [+{}] [{}]".format(
            stamp.strftime("%Y-%m-%d %H:%M:%S"), duration, self.id
        )

        for object_to_log in args:
            if isinstance(object_to_log, str):
                obj_log += self.__log_string(object_to_log)
            else:
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
            raise FileNotFoundError(
                "can't access the log file: {}, stopping execution for job {}".format(
                    self.log_file, str(self.id)
                )
            )

    def __log_object(self, obj, prefix: str = "+", header: str = "", indent: int = 4):
        return self.__log_string(
            header
            + json.dumps(vars(obj), indent=indent, cls=helpers.StirlingJSONEncoder),
            prefix,
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
                    "unable to download source file from URL {}, stopping execution for job {}".format(
                        self.source, str(self.id)
                    )
                )
        self.log("File to processed will be: " + str(self.source))

        # Get a full path to name our source file when we move it. We'll use this
        # value later on as an input filename for specific commands.
        incoming_filename = Path(
            str(self.output_directory) + "/source" + Path(self.source).suffix
        )
        source_output_directory = self.output_directory / "source"

        if not self.source_copy_disable:
            # Unless this is a simulation or we explicitly disabled it, copy the source
            # file to the output directory as 'source'
            source_output_directory.mkdir(parents=True, exist_ok=True)

            shutil.copyfile(Path(self.source).absolute(), incoming_filename)
            if not self.source_delete_disable:
                # Don't delete the incoming source file, in case we're testing.
                os.remove(self.source)

            self.source = incoming_filename

    def __get_output_directory(self):
        if self.output_directory is None or self.output_directory == Path("."):
            self.output_directory = Path(Path.cwd() / "output" / str(self.id))

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
        assert self.output_directory.is_dir(), AssertionError(
            "could not find the path {} for output files for job {}".format(
                str(self.output_directory), str(self.id)
            ),
        )

        # Make sure we can write to the directory for the output files
        assert os.access(self.output_directory, os.W_OK), AssertionError(
            "could not write to path {} for output files for job {}".format(
                str(self.output_directory), str(self.id)
            )
        )

    def __log_string(self, msg: str, line_identifier: str = "+", indent: int = 4):
        new_line_string = "\n" + line_identifier + " " * indent
        return new_line_string + new_line_string.join(msg.splitlines())

    def __is_url(self):
        try:
            result = urlparse.urlparse(self.source)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False
