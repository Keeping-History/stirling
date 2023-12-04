from enum import auto
from pathlib import Path
from typing import Dict, List

from strenum import StrEnum

from stirling.core import StirlingClass
from stirling.dependencies import StirlingDependency


class StirlingCommandStatus(StrEnum):
    """StirlingCommandStatus is the status of a current command."""

    RECEIVED = auto()
    QUEUED = auto()
    RUNNING = auto()
    CANCELLED = auto()
    FAILED = auto()
    SUCCEEDED = auto()


class StirlingCommandTarget(StrEnum):
    """StirlingCommandStatus is the status of a current command."""

    LOCAL = auto()


class StirlingCommand(StirlingClass):
    """StirlingCommand is the base class for command objects. These command
    objects will be converted into specific commands to run for
    a specific plugin/step in a job.json. A StirlingCommand includes the full command
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
    what kind of environments can run a job.json.

    Attributes:
        name (str): The name of plugin that created the command.
        dependency (StirlingDependency): The binary dependency to receive the command.
        priority (int): The priority of the command, this is optional.
            After commands are sorted based on their dependencies, they will
            be sorted by priority. The default is 0, which is the highest
            priority.
        expected_outputs (str): The output (filename, directory or glob pattern) that we
         expect to be created when this command is run. This is optional, and the
         default is None.
        depends_on (list): A list of plugins that this plugin depends on before
            it can run. This is optional, and the default is None.
        log (str): The raw, text log output from the command.
        status (StirlingCommandStatus): The status of the command. The default
            is QUEUED
    """

    name: str
    dependency: StirlingDependency | None = None
    arguments: Dict[str, str] | None = None
    depends_on: List[str] | None = None
    expected_outputs: List[str | Path] | None = None
    log: str | None = None
    status: StirlingCommandStatus = StirlingCommandStatus.RECEIVED
    priority: int = 0
    target: StirlingCommandTarget = StirlingCommandTarget.LOCAL

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


class StirlingCommandQueue(StirlingClass):
    commands: List[StirlingCommand] = []
    target: StirlingCommandTarget = StirlingCommandTarget.LOCAL

    def status(self):
        if len(self.commands) == 0:
            # If the command queue is empty, then we set it as received.
            return StirlingCommandStatus.RECEIVED
        elif any(c.status == StirlingCommandStatus.FAILED for c in self.commands):
            # If any command fails, then the whole queue should be considered as failed also.
            return StirlingCommandStatus.FAILED
        elif any(c.status == StirlingCommandStatus.CANCELLED for c in self.commands):
            # If any command is cancelled, then the whole queue should be considered as cancelled also.
            return StirlingCommandStatus.CANCELLED
        elif all(c.status == StirlingCommandStatus.SUCCEEDED for c in self.commands):
            # The queue is successful only when all commands succeed.
            return StirlingCommandStatus.SUCCEEDED
        elif any(c.status == StirlingCommandStatus.RUNNING for c in self.commands):
            # If any command is running, and none of the jobs have been cancelled or failed, then the queue is running.
            return StirlingCommandStatus.RUNNING
        else:
            # The default status of a queue is queued.
            return StirlingCommandStatus.QUEUED

    def get(self, command: int | List[str] | str):
        if isinstance(command, int):
            return self.commands[command]
        if isinstance(command, str):
            return [c for c in self.commands if c.name == command]
        if isinstance(command, list):
            items = []
            for c in command:
                items.extend([c for c in self.commands if c.name == command])
            return items

    def add(self, command: StirlingCommand | List[StirlingCommand]):
        if isinstance(command, list):
            for c in command:
                c.queued()
            self.commands.extend(command)
            return
        command.queued()
        self.commands.append(command)

    def parse(self, command: int | List[str] | str):
        command = self.get(command)

    def sort(self):
        self.commands.sort(key=lambda x: x.priority, reverse=True)

    def run(self, index: int | List[int] | None = None):
        self.sort()
        if isinstance(index, int):
            return self.commands[index].run(self.target)
        if isinstance(index, list):
            return [self.commands[c].run(self.target) for c in index]

        return [c.run(self.target) for c in self.commands]
