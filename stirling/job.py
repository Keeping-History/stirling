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
from stirling.config import StirlingConfig
from stirling.core import StirlingClass
from stirling.encodings import StirlingJSONEncoder
from stirling.errors import CommandError, MissingFrameworkError
from stirling.frameworks.base import StirlingMediaFramework, StirlingMediaInfo
from stirling.frameworks.get import available_frameworks, get_framework
from stirling.logger import (
    StirlingLoggerLevel,
    get_job_logger,
)
from stirling.plugins.core import StirlingPlugin, StirlingPluginAssets
from stirling.logger import StirlingLoggerColors as LC

abc = "1234"


@dataclass_json
@dataclass
class StirlingJobOptions(StirlingClass):
    """A class that contains all the options that can be used by the StirlingJob.

    Attributes:

        job_file (pathlib.Path | str): A JSON document describing the job. This
            file is created when the job is created, and updated as the job
            progresses. Alternately, a job can be created from a JSON file
            passed in as this argument. Strings will be interpreted into a
            Path; if no root path is given then the current The default is None, which will cause
            a file named 'job.json' to be created in the output directory.
        log_file (pathlib.Path | str): The filename to output logs from the job.
        input_directory (pathlib.Path): The folder prefix where incoming files
            are located. Defaults to the current working directory
        source_delete (bool): Delete the temporary incoming source file
            when finished. By default, the temporary incoming source file is not
            deleted.
        output_directory (pathlib.Path | str): The directory to output the package.
            Defaults to a folder named with the job's ID (a random UUID) in the
            current working folder.
        output_annotations_directory (pathlib.Path | str): The directory prefix to use when
            storing annotations. Defaults to `annotations`.
        source_copy (bool): When a job is completed, a copy of the
            media file as it was uploaded is created in the output directory
            as "source". This can be disabled.
        log_level (StirlingLoggerLevel): set the log level for the job. Defaults to INFO.

    """

    job_file: Path | None = None
    log_file: Path | None = None
    input_directory: Path | None = None
    source_delete: bool | None = None
    output_directory: Path | None = None
    output_annotations_directory: Path | None = None
    source_copy: bool | None = None
    log_level: StirlingLoggerLevel | int | None = None
    framework: str | None = None


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
        framework (core.StirlingMediaFramework): The framework to use to process media
            files. Defaults to FFMpeg.
        options (StirlingJobOptions): An object containing the configuration for the
            job. This is created from the StirlingConfig object, and is passed to
            the framework when the job is created. Variables include:

    Raises:
        FileNotFoundError: _description_

    """

    # Required fields
    source: Union[Path, str]

    # Stirling Engine Configuration
    config: dict = field(default_factory=dict)

    # Job config
    options: StirlingJobOptions | None = None

    # Optional fields
    id: UUID = uuid4()
    time_start: datetime = datetime.now()
    time_end: datetime = datetime.now()
    duration: float = 0.0

    # Framework and media info
    framework: StirlingMediaFramework | None = field(init=False, default=None)
    media_info: StirlingMediaInfo | None = field(init=False, default=None)

    # Plugins to load
    plugins: List[StirlingPlugin] | None = field(default_factory=list)

    # Commands to run
    commands: List[StirlingCommand] | None = field(default_factory=list)

    # Expected Outputs
    outputs: List | None = field(default_factory=list)

    def __post_init__(self):
        """Set up the job after it is created.

        The __post_init__ function is called after the object is created. Here,
        we attempt to set up the job by doing things like creating the output
        folder, attempt to get the source file (either from a local or remote
        store, based on the Path scheme), and then probe the source file to
        determine its metadata (like dimensions, bitrate, duration, etc).
        """

        super().__post_init__()

        # Load the config client to get Job setting defaults
        self._config_client = StirlingConfig()
        if not self.config:
            self.config = self._config_client.get()

        # Set our job options here
        default_job_options = StirlingConfig().get_json("job")
        self.options = self.options or StirlingJobOptions().from_json(
            default_job_options
        )

        # Setup our output directory
        self._get_output_directory()

        # Logging
        self._logger = get_job_logger(
            log_file=self.options.log_file,
            log_level=self.options.log_level,
            time_start=self.time_start,
            job_id=self.id,
        )

        self._logger.info("Starting job.")
        self._logger.info("Job options loaded: ", self.options)
        self._logger.info(
            f"Output Directory will be: {str(self.options.output_directory.resolve())}"
        )

        # Validate our incoming source file
        self._logger.info(
            f"Validating requested source file: {str(self.source)}"
        )
        self.source = self._get_source(self.source)

        self._logger.info(f"File to processed will be: {str(self.source)}")

        # Check if the framework requested for the job is available.
        self._logger.info(
            f"Requested framework is: {LC.highlight(self.options.framework)}"
        )
        if self.options.framework not in available_frameworks():
            self._logger.error(
                f"The requested framework {str(self.options.framework)} was not found. This is an unrecoverable error."
            )
            raise MissingFrameworkError

        # Get and initialize the framework.
        framework_class = get_framework(self.options.framework)
        self.framework = framework_class(source=self.source)

        # Probe the source file
        self.media_info = self.framework.probe(source=str(self.source))
        self._logger.info(f"Media file {self.source} probed.")
        self._logger.info("Probe results: ", self.media_info)

        # The source file is now ready for processing, and the job has finished loading.
        self._logger.info(
            f"Job has successfully started up; source file {self.source} is ready for processing."
        )

        self.write()

    def close(self) -> None:
        """Close out the job and update its metadata"""

        if self.options.source_delete:
            os.remove(self.source)

        self.time_end = datetime.now()
        self.duration = (self.time_end - self.time_start).total_seconds()
        self._logger.info(
            f"Ending job {self.id} at {self.time_end},"
            f"total duration: {self.duration}"
        )
        if self.options.log_level == StirlingLoggerLevel.DEBUG:
            self._logger.debug("Job Definition:", self)

    def run(self) -> None:
        """Run all the commands in the job."""

        cmd_holder = []
        for cmd in self.commands:
            # Check if we can probe the input file.
            cmd.status = StirlingCommandStatus.RUNNING
            short_cmd = shorten(cmd.command, width=20)
            self._logger.info(
                f"Starting command {short_cmd} for plugin {cmd.name}"
            )
            cmd_output = getstatusoutput(cmd.command)
            cmd.log = cmd_output[1]
            short_output = shorten(cmd.command, width=20)
            if cmd_output[0] != 0:
                cmd.status = StirlingCommandStatus.FAILED
                self._logger.error(
                    f"Command {short_cmd} for plugin {cmd.name} failed."
                )
                self._logger.debug(
                    f"Command for plugin {cmd.name}:", cmd.command
                )
                self._logger.debug("Output:", cmd.log)
                raise CommandError(
                    f"Command {short_cmd} for plugin {cmd.name} failed."
                )

            cmd.status = StirlingCommandStatus.SUCCEEDED

            self._logger.info(
                f"Command {shorten(cmd.command, width=20)} for plugin {cmd.name} succeeded. Output: ",
                cmd.log,
            )
            self.write()

            cmd_holder.append(cmd)

        self.commands = cmd_holder

    def write(self) -> None:
        """Make a snapshot of the job (in JSON format) to the job log file."""
        with open(self.options.job_file, "w", encoding="utf-8") as output_file:
            output_file.write(dumps(self, indent=4, cls=StirlingJSONEncoder))

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
            self._logger.info(f"Added plugin '{plugin.name}'.")
        self._parse()
        self.write()

    def _get_source(self, source: Path | None) -> Path:
        """Get the source file for the job.

        The source file is the only required field for a Stirling Job. If
            it doesn't exist, or is inaccessible, then the job will fail.

        Args:
            source (str): The source file for the job.
        """

        # If the incoming source is a URL, then let's download it.
        if url_validator(str(self.source), public=False):
            self._get_source_from_url(source)

        if self.options.source_copy:
            # Get a full path to name our source file when we move it. We'll use this
            # value later on as an input filename for specific commands.
            source_output_directory = self.options.output_directory / "source"

            # Unless explicitly disabled, copy the source
            # file to the output directory as 'source'
            source_output_directory.mkdir(parents=True, exist_ok=True)
            incoming_filename = (
                self.options.output_directory / "source" / self.source.name
            )
            copyfile(Path(self.source).absolute(), incoming_filename)
            return incoming_filename.resolve()

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

        if (
            not hasattr(self.options, "output_directory")
            or self.options.output_directory is None
        ):
            self.options.output_directory = (
                Path(self.source).parent / "output" / str(self.id)
            )

        self.options.output_directory = Path(
            self.options.output_directory
        ).resolve()

        if not self.options.output_directory.is_dir():
            self.options.output_directory.mkdir(parents=True, exist_ok=True)
            annotations_output_directory = (
                self.options.output_directory
                / self.options.output_annotations_directory
            )
            annotations_output_directory.mkdir(parents=True, exist_ok=True)

        self.options.log_file = (
            self.options.output_directory / self.options.log_file
        )
        self.options.job_file = (
            self.options.output_directory / self.options.job_file
        )

        # Make sure we have a directory for the output files
        assert self.options.output_directory.is_dir(), AssertionError(
            f"could not find the path {str(self.output_directory)} \
                for output files for job {str(self.id)}"
        )

        # Make sure we can write to the directory for the output files
        assert os.access(
            self.options.output_directory, os.W_OK
        ), AssertionError(
            f"could not write to path {str(self.output_directory)} \
                for output files for job {str(self.id)}"
        )

        # Make sure we can write to the directory for the output files by
        # testing out log file
        with open(
            str(self.options.log_file), "a", encoding="utf-8"
        ) as test_file:
            assert test_file.writable(), AssertionError(
                f"could not write to the log file the path \
                    {str(self.options.log_file)} for job {str(self.id)}"
            )

    def _parse(self):
        """Parse the job and plugins to generate a list of commands to run."""

        # Clear the previous expected outputs
        self.outputs = None

        # Create some holder variables
        cmd_sort_holder = {}
        cmd_output_holder = []

        for plugin in self.plugins:
            self._logger.info(f"Parsing plugin '{plugin.name}' commands.")
            plugin.cmd(self)

            # Sort each command in the plugin by its priority
            self.commands.sort(key=lambda x: x.priority, reverse=True)

            # Create a holder, so we can run a topographical sort on the commands
            for cmd in self.commands:
                if len(cmd.depends_on) > 0:
                    cmd_sort_holder[cmd.name] = cmd.depends_on

            if cmd_sort_holder:
                self._logger.info(
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
                        self._logger.info(
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
        self._logger.info(f"Plugins added {len(self.commands)} commands.")
