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
from urllib.parse import urlsplit

import networkx
import requests
import validators

from core import definitions, helpers, probe

# TODO: Need this later for merging in a json job file.
# from mergedeep import merge


@dataclass
class StirlingJob(definitions.StirlingClass):
    """A collection of arguments, plugins, and commands to process on a source file.

    A StirlingJob contains the base arguments, functions and information
    necessary to start up a Stirling job. These includes things like
    input and output file and directories, and other options related to the
    running of the job.


    Attributes:
        source (str): The input source filename (required)
        id (uuid.UUID): The unique ID of the job. We create a random UUID v4
            whenever a job is created, however a custom one can be supplied so
            long as it is a UUID v4.
        time_start (datetime.datetime): The start time of the job in UTC.
        time_end (datetime.datetime): The end time of the job in UTC.
        duration (float): the length of the job run time, in seconds.
        job_file (pathlib.Path): A JSON document describing the job. This
            file is created when the job is created, and updated as the job
            progresses. Alternately, a job can be created from a JSON file
            passed in as this argument. Strings will be interpreted into a
            Path; if no root path is given then the current The default is None, which will cause
            a file named 'job.json' to be created in the output directory.
        log_file (pathlib.Path): The filename to output logs from the job.
        input_directory (pathlib.Path): The folder prefix where incoming files
            are located. Defaults to the current working directory
        source_delete_disable (bool): Delete the temporary incoming source file
            when finished. By default, the temporary incoming source file is
            deleted.
        output_directory (pathlib.Path): The directory to output the package.
            Defaults to a folder named with the job's ID (a random UUID) in the
            current working folder.
        output_annotations_directory (str): The directory prefix to use when
            storing annotations. Defaults to `annotations`.
        source_copy_disable (bool): When a job is completed, a copy of the
            video file as it was uploaded is created in the output directory
            as "source". This can be disabled.
        simulate (bool): A debugging option that attempts to setup a full
            job without actually doing any of the external
            transcoding/extraction or running and plugins.. This is poorly
            supported and will be removed in a future version.
        debug (bool): Enable additional debugging output
        media_info (probe.StirlingMediaInfo): Contains metadata about the
            source media file, after it is probed.

    Raises:
        FileNotFoundError: _description_

    """ """"""

    source: str  # required
    id: uuid.UUID = uuid.uuid4()
    time_start: datetime = datetime.now()
    time_end: datetime = None
    duration: float = 0.0
    job_file: Path = None
    log_file: Path = "job.log"
    input_directory: Path = Path(os.getcwd())
    source_delete_disable: bool = True
    output_directory: Path = None
    output_annotations_directory: str = "annotations"
    source_copy_disable: bool = True
    simulate: bool = False
    debug: bool = True
    media_info: probe.StirlingMediaInfo = None

    # Private fields
    _plugins: List = field(default_factory=list)
    _outputs: List = field(default_factory=list)
    _commands: List[definitions.StrilingCmd] = field(default_factory=list)

    def __post_init__(self):
        """Setup the job after it is created.

        The __post_init__ function is called after the object is created. Here,
        we attempt to setup the job by doing things like creating the output
        folder, attempt to get the source file (either from a local or remote
        store, based on the Path scheme), and then probe the source file to
        determine its metadata (like dimensions, bitrate, duration, etc).

        As well, if we provide a JSON job file, we attempt to load that in and
        set the job up based on that.
        """
        # If the job file has been passed in, then load it.
        # Currently, we are setting the Job File as a default Path. We should
        # instead default this field to None, and check here if it is set
        # otherwise (and then load the job file).
        if self.job_file is not None:
            self.load()
        else:
            self.job_file = Path("./job.json")

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
        print(self.media_info)
        self.log("Media file {} probed: ".format(self.source), self.media_info)
        self.write()

    @property
    def commands(self):
        """Get a list of commands to run.

        Returns:
            list[StrilingCmd]: A list of commands to run
        """

        return self._commands

    @property
    def outputs(self):
        """Get a list of expected outputs from job and plugin commands.
        are run.

        When a plugin generates a Command, it is also responsible for adding
        each file (or a directory) that it expects to be generated by that
        command for that plugin. Once all of the commands are run and the
        job is ready to be closed, the actual output from each of the commands
        will be checked against the expected outputs (here) to ensure that al
        of the expected files were generated and the commands ran successfully.
        Note: A job will not fail if there are missing or extra files generated,
        but it should be noted to the user that a plugin or command may have
        failed.

        Returns:
            list[str]: A list of expected outputs from every command
                in the job after it is run.
        """

        return self._outputs

    @property
    def plugins(self):
        """Return a list of plugins add to the job.

        We attach Plugins to the job by using the plugins() setter. This
        property returns the contents of the private _plugins list.

        Returns:
            list[]: _description_
        """

        return self._plugins

    def add_plugins(self, *args):
        """Add new plugins to the job.

        Call this It is not currently possible to remove plugins from a job once they
        have been added.

        Args:
            *args: A single plugin, or list of plugins to add to the job.
        """

        for plugin in args:
            self._plugins.append(plugin)
            self.log('Added plugin "{}". '.format(plugin.plugin_name))
        self.__parse()
        self.write()

    def load(self):
        """Load a job from the specified JSON job file."""
        # TODO: Implement the actual merge from a JSON job file
        #  This whole function is just a
        #  placeholder stub
        # if self.job_file.is_file():
        #   with open(self.job_file) as json_file:
        #   # Load the file into our Job Object
        #       new_job = json.load(json_file)
        #       job = merge({}, self, new_job)
        #       self.log("Loaded job: ", job)
        pass

    def close(self):
        """Close out the job and update its metadata"""

        self.time_end = datetime.now()
        self.duration = (self.time_end - self.time_start).total_seconds()
        self.log(
            "Ending job {} at {}, total duration: {}".format(
                self.id, self.time_end, self.duration
            ),
        )
        self.write()

    def run(self):
        """Run all the commands in the job."""

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

        self._commands = cmd_holder

    def write(self):
        """Log an object (in JSON format) to the job log file."""

        output_file = open(self.job_file, "w")
        output_file.write(json.dumps(self, indent=4, cls=helpers.StirlingJSONEncoder))
        output_file.close()

    def log(self, message: str, *args):
        """Write a message to the log file.

        Args:
            message (str): The message to write to the log file.
            *args (object): Any additional objects to log to the file (as JSON).
        """

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

    def __log_string(self, msg: str, line_identifier: str = "+", indent: int = 4):
        """Log a string to the job log file."""

        new_line_string = "\n" + line_identifier + " " * indent
        return new_line_string + new_line_string.join(msg.splitlines())

    def __log_object(self, obj, prefix: str = "+", header: str = "", indent: int = 4):
        """Log an object to the job log file.

        Args:
            obj: The object to log
            prefix (str): The prefix to use for each line
            header (str): A header to print before each line
            indent (int): The number of spaces to indent each line of JSON

        Returns:
            str: The object as a string for logging
        """

        return self.__log_string(
            header
            + json.dumps(vars(obj), indent=indent, cls=helpers.StirlingJSONEncoder),
            prefix,
            indent,
        )

    def __get_source(self):
        """Get the source file for the job.

        The source file is the only required field for a Stirling Job. If
            it doesn't exist, or is inaccessible, then the job will fail.

        Raises:
            FileNotFoundError: _description_
        """

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
        """Get the full path to the output directory for this job.

        We need to create the output directory if it doesn't exist, and
        ensure that we can create other directories in that path.
        """

        if self.output_directory is None or self.output_directory == Path("."):
            self.output_directory = Path(Path.cwd() / "output" / str(self.id))

        # Make the output directory, if it doesn't exist.
        if not self.output_directory.is_dir():
            self.output_directory.mkdir(parents=True, exist_ok=True)
            annotations_output_directory = (
                self.output_directory / self.output_annotations_directory
            )
            annotations_output_directory.mkdir(parents=True, exist_ok=True)

        print(self.job_file)
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

        # Make sure we can write to the directory for the output files by
        # testing out log file
        test_file = open(str(self.log_file), "a")

        assert test_file.writable(), AssertionError(
            "could not write to the log file the path {} for job {}".format(
                str(self.log_file), str(self.id)
            ),
        )

        test_file.close()

    def __parse(self):
        """Parse the job and plugins to generate a list of commands to run."""

        # Clear the previous expected outputs
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
        self._commands = cmd_output_holder
        self.log("Plugins added {} commands.".format(len(self.commands)))
