import os
import re
from dataclasses import field
from datetime import datetime
from json import dumps
from pathlib import Path
from shutil import copyfile
from subprocess import getstatusoutput
from textwrap import shorten
from typing import List, Union
from urllib.parse import urlsplit
from uuid import UUID, uuid4

from dataclasses_json import dataclass_json
from networkx import DiGraph, topological_sort
from pydantic.dataclasses import dataclass
from requests import get as get_url
from requests.exceptions import HTTPError, RequestException
from validators import url as url_validator

from stirling.command.base import StirlingCommand, StirlingCommandStatus
from stirling.core import StirlingClass
from stirling.encodings import StirlingJSONEncoder
from stirling.errors import CommandError
from stirling.frameworks.base import StirlingMediaFramework, StirlingMediaInfo
from stirling.frameworks.ffmpeg import StirlingMediaFrameworkFFMpeg
from stirling.logger import StirlingLogger
from wip.plugins import StirlingPlugin, StirlingPluginAssets


@dataclass_json
@dataclass
class StirlingJob(StirlingClass):
    """A collection of arguments, plugins, and commands to process on a source file.

    A StirlingJob contains the base arguments, functions and information
    necessary to start up a Stirling job. These include things like
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
            media file as it was uploaded is created in the output directory
            as "source". This can be disabled.
        simulate (bool): A debugging option that attempts to set up a full
            job without actually doing any of the external
            transcoding/extraction or running and plugins. This is poorly
            supported and will be removed in a future version.
        debug (bool): Enable additional debugging output
        media_info (core.StirlingMediaInfo): Contains metadata about the
            source media file, after it is probed.
        plugins (list): A list of plugins to run on the source file. To attach
            Plugins to the job, use the add_plugins() method.
        commands (list): A list of commands to run on the source file.
            When a plugin generates a Command, it is also responsible for adding
            each file (or a directory) that it expects to be generated by that
            command for that plugin.
        outputs (list): Once all commands are run and the
            job is ready to be closed, the actual output from each of the commands
            will be checked against the expected outputs (here) to ensure that al
            of the expected files were generated and the commands ran successfully.
            Note: A job will not fail if there are missing or extra files generated,
            but it should be noted to the user that a plugin or command may have
            failed.


    Raises:
        FileNotFoundError: _description_

    """

    # Required fields
    source: Union[Path, str]

    # Optional fields
    id: UUID = uuid4()
    time_start: datetime = datetime.now()
    time_end: datetime = datetime.now()
    duration: float = 0.0
    job_file: Path = Path("./job.json")
    log_file: Path = Path("./job.log")
    input_directory: Path = Path(os.getcwd())
    source_delete_disable: bool = True
    output_directory: Path | None = None
    output_annotations_directory: str = "annotations"
    source_copy_disable: bool = False
    simulate: bool = False
    debug: bool = True

    framework: StirlingMediaFramework | None = field(init=False, default=None)
    media_info: StirlingMediaInfo | None = field(init=False, default=None)

    outputs: List | None = field(default_factory=list)
    commands: List[StirlingCommand] | None = field(default_factory=list)
    plugins: List[StirlingPlugin] | None = field(default_factory=list)

    def __post_init__(self):
        """Set up the job after it is created.

        The __post_init__ function is called after the object is created. Here,
        we attempt to set up the job by doing things like creating the output
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
        self.load()

        # Convert our source to a Path
        if not isinstance(self.source, Path):
            raise ValueError("Source must be a valid Path object or string.")

        # Setup our output directory
        self._get_output_directory()

        # Logging
        self._logger = StirlingLogger(
            job_id=self.id,
            log_file=self.log_file,
            time_start=self.time_start,
            debug=self.debug,
        )

        self._logger.log("Starting job with definition: ", self)
        self._logger.log(
            f"Output Directory will be: {str(self.output_directory)}"
        )

        # Validate our incoming source file
        self._get_source(self.source)
        # Probe the source file
        # TODO: Remove this and make the framework more generic
        self.framework = StirlingMediaFrameworkFFMpeg()
        self.media_info = self.framework.probe(source=str(self.source))

        self._logger.log(f"Media file {self.source} probed:", self.media_info)
        self.write()

    def get_plugin(self, plugin_name: str) -> StirlingPlugin:
        """Get a plugin by name.

        Args:
            plugin_name (str): The name of the plugin to get
        """
        return_plugin = None
        for plugin in self.get_plugins:
            if plugin.name == plugin_name:
                return_plugin = plugin
        return return_plugin

    def get_plugin_assets(
        self, plugin_name: str
    ) -> List[StirlingPluginAssets] | None:
        """Get all the assets of a plugin.

        Args:
            plugin_name (str): The name of the plugin to get.
        """

        plugin = self.get_plugin(plugin_name)
        return plugin.assets

    def get_plugin_asset(self, plugin_name: str, asset_name: str) -> Path:
        """Get a plugin's asset by name.

        Args:
            plugin_name (str): The name of the plugin the asset belongs to.
            asset_name (str): The name of the asset to get.
        """

        assets = self.get_plugin_assets(plugin_name)

        return_asset_path = Path()
        for asset in assets:
            if asset.name == asset_name:
                return_asset_path = asset.path
            else:
                raise ValueError("Asset not found")

        return return_asset_path

    def add_plugins(self, *args) -> None:
        """Add new plugins to the job.

        Call this It is not currently possible to remove plugins from a job once they
        have been added.

        Args:
            *args: A single plugin, or list of plugins to add to the job.
        """

        for plugin in args:
            self.plugins.append(plugin)
            self._logger.log(f"Added plugin '{plugin.name}'.")
        self._parse()
        self.write()

    def close(self) -> None:
        """Close out the job and update its metadata"""

        if not self.source_delete_disable:
            # Don't delete the incoming source file, in case we're testing.
            os.remove(self.source)

        self.time_end = datetime.now()
        self.duration = (self.time_end - self.time_start).total_seconds()
        self._logger.log(
            f"Ending job {self.id} at {self.time_end}, total duration: {self.duration}"
        )
        self.write()

    def run(self) -> None:
        """Run all the commands in the job."""

        cmd_holder = []
        for cmd in self.commands:
            # Check if we can probe the input file.
            cmd.status = StirlingCommandStatus.RUNNING
            short_cmd = shorten(cmd.command, width=20)
            self._logger.log(
                f"Starting command {short_cmd} for plugin {cmd.name}"
            )
            cmd_output = getstatusoutput(cmd.command)
            cmd.log = cmd_output[1]
            short_output = shorten(cmd.command, width=20)
            if cmd_output[0] != 0:
                cmd.status = StirlingCommandStatus.FAILED
                self._logger.log(
                    f"Command {short_output} for plugin {cmd.name} failed."
                )
                self._logger.log(f"Command for plugin {cmd.name}:", cmd.command)
                self._logger.log("Output:", cmd.log)
                raise CommandError(
                    f"Command {short_cmd} for plugin {cmd.name} failed."
                )

            cmd.status = StirlingCommandStatus.SUCCEEDED

            self._logger.log(
                f"Command {shorten(cmd.command, width=20)} for plugin {cmd.name} succeeded. Output: ",
                cmd.log,
            )
            self.write()

            cmd_holder.append(cmd)

        self.commands = cmd_holder

    def write(self) -> None:
        """Log an object (in JSON format) to the job log file."""

        with open(self.job_file, "w", encoding="utf-8") as output_file:
            output_file.write(dumps(self, indent=4, cls=StirlingJSONEncoder))

    def _get_source(self, source: Path | None) -> None:
        """Get the source file for the job.

        The source file is the only required field for a Stirling Job. If
            it doesn't exist, or is inaccessible, then the job will fail.

        Args:
            source (str): The source file for the job.
        """

        # If the incoming source is a URL, then let's download it.
        if url_validator(str(self.source), public=False):
            self._get_source_from_url(source)
        self._logger.log(f"File to processed will be: {str(self.source)}")

        if not self.source_copy_disable:
            # Get a full path to name our source file when we move it. We'll use this
            # value later on as an input filename for specific commands.
            source_output_directory = self.output_directory / "source"

            # Unless explicitly disabled, copy the source
            # file to the output directory as 'source'
            source_output_directory.mkdir(parents=True, exist_ok=True)
            incoming_filename = (
                self.output_directory / "source" / self.source.name
            )
            copyfile(Path(self.source).absolute(), incoming_filename)

            self.source = incoming_filename

    def _get_source_from_url(self, source):
        # TODO: We need to really fix the way we handle failures here.
        try:
            response = get_url(str(self.source), timeout=10)
        except RequestException as err:
            raise err

        if response.status_code != 200:
            raise HTTPError(
                f"Error downloading {self.source}: {response.status_code}"
            )

        reported_filename = os.path.basename(urlsplit(source).path)
        incoming_filename = Path(
            self.output_directory / re.sub(r"[^\w\d-]", "_", reported_filename)
        )

        self.source = incoming_filename
        try:
            open(self.source, "wb").write(response.content)
        except Exception as err:
            raise err

    def _get_output_directory(self):
        """Get the full path to the output directory for this job.

        We need to create the output directory if it doesn't exist, and
        ensure that we can create other directories in that path.
        """

        # Make the output directory, if it doesn't exist.

        if self.output_directory is None:
            self.output_directory = (
                Path(self.source).parent / "output" / str(self.id)
            )

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
            f"could not find the path {str(self.output_directory)} \
                for output files for job {str(self.id)}"
        )

        # Make sure we can write to the directory for the output files
        assert os.access(self.output_directory, os.W_OK), AssertionError(
            f"could not write to path {str(self.output_directory)} \
                for output files for job {str(self.id)}"
        )

        # Make sure we can write to the directory for the output files by
        # testing out log file
        with open(str(self.log_file), "a", encoding="utf-8") as test_file:
            assert test_file.writable(), AssertionError(
                f"could not write to the log file the path \
                    {str(self.log_file)} for job {str(self.id)}"
            )

    def _parse(self):
        """Parse the job and plugins to generate a list of commands to run."""

        # Clear the previous expected outputs
        self.outputs = None

        # Create some holder variables
        cmd_sort_holder = {}
        cmd_output_holder = []

        for plugin in self.plugins:
            self._logger.log(f"Parsing plugin '{plugin.name}' commands.")
            plugin.cmd(self)

            # Sort each command in the plugin by its priority
            self.commands.sort(key=lambda x: x.priority, reverse=True)

            # Create a holder, so we can run a topographical sort on the commands
            for cmd in self.commands:
                if len(cmd.depends_on) > 0:
                    cmd_sort_holder[cmd.name] = cmd.depends_on

            if cmd_sort_holder:
                self._logger.log(
                    f"Parsing plugin '{plugin.name}' dependencies {plugin.depends_on}."
                )

            # Sort the commands by their dependencies
            cmd_sort_list = list(
                reversed(list(topological_sort(DiGraph(cmd_sort_holder))))
            )

            # Reorder the commands based on the topographical sort
            for v in cmd_sort_list:
                for cmd in self.commands:
                    if cmd.name == v:
                        self._logger.log(
                            f'Appending command for plugin "{cmd.name}": {cmd.command}.'
                        )
                        cmd_output_holder.append(cmd)
                        self.outputs.append(str(cmd.expected_output))
            self.commands = cmd_output_holder

        # Create the necessary folders for the plugin outputs
        for output in self.outputs:
            output_dir = Path(os.path.dirname(Path(output)))
            output_dir.mkdir(parents=True, exist_ok=True)

        # Set the commands to the sorted list
        self._logger.log(f"Plugins added {len(self.commands)} commands.")
