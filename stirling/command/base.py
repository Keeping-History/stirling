from enum import auto
from typing import Dict, List

from pydantic.dataclasses import dataclass
from strenum import StrEnum

from stirling.dependencies import StirlingDependency
from stirling.core import StirlingClass


class StirlingCommandStatus(StrEnum):
    """StirlingCommandStatus is the status of a current command."""

    RECEIVED = auto()
    QUEUED = auto()
    RUNNING = auto()
    CANCELLED = auto()
    FAILED = auto()
    SUCCEEDED = auto()


@dataclass(kw_only=True)
class StirlingCommand(StirlingClass):
    """StirlingCommand is the base class for command objects. These command
    objects will be converted into specific commands to run for
    a specific plugin/step in a job. A StirlingCommand includes the full command
    to run in "cli" style, and the raw output from the command.

    The goal is to eliminate Python-only media packages, and run jobs in any
    environment, and in any configuration: local server, cloud provider,
    container infrastructure or a combination thereof. Therefore, regardless
    of the underlying hardware or operating runtime, we can provide a consistent
    interface to any number of Media Frameworks or Encoder.

    Encoders are highly-tuned, low-level applications that are designed to
    perform as efficiently as possible. Using an additional package to wrap
    a Media Framework (such as FFMPeg) adds additional overhead, and using
    bindings to a low-level codec library (such as `libav`) limits options for
    what kind of environments can run a job.

    Attributes:
        name (str): The name of plugin that created the command.
        dependency (StirlingDependency): The binary dependency to receive the command.
        priority (int): The priority of the command, this is optional.
            After commands are sorted based on their dependencies, they will
            be sorted by priority. The default is 0, which is the highest
            priority.
        expected_output (str): The output (filename, directory or glob pattern) that we expect to
            be created when this command is run. This is optional, and the default
            is None.
        depends_on (list): A list of plugins that this plugin depends on before
            it can run. This is optional, and the default is None.
        log (str): The raw, text log output from the command.
        status (StirlingCommandStatus): The status of the command. The default
            is QUEUED
    """

    name: str | None
    dependency: StirlingDependency
    arguments: Dict[str, str]
    expected_output: str | None
    depends_on: List[str] | None
    log: str | None
    status: StirlingCommandStatus = StirlingCommandStatus.RECEIVED
    priority: int = 0

    def receive(self) -> StirlingCommandStatus:
        """
        Receive a command.
        """
        self.status = StirlingCommandStatus.RECEIVED
        return self.status

    def queue(self) -> StirlingCommandStatus:
        """
        Queue a command.
        """
        self.status = StirlingCommandStatus.QUEUED
        return self.status

    def run(self) -> StirlingCommandStatus:
        """
        Run the command.
        """
        self.status = StirlingCommandStatus.RUNNING
        return self.status

    def cancel(self) -> StirlingCommandStatus:
        """
        Run the command.
        """
        self.status = StirlingCommandStatus.CANCELLED
        return self.status

    def fail(self) -> StirlingCommandStatus:
        """
        Run the command.
        """
        self.status = StirlingCommandStatus.FAILED
        return self.status

    def succeed(self) -> StirlingCommandStatus:
        """
        Run the command.
        """
        self.status = StirlingCommandStatus.SUCCEEDED
        return self.status
