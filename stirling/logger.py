from dataclasses import field
from datetime import datetime
from enum import Enum
from json import dumps
from pathlib import Path
from uuid import UUID

from colored import attr, bg, fg
from pydantic.dataclasses import dataclass

from stirling.core import StirlingClass
from stirling.encodings import StirlingJSONEncoder


class StirlingLoggerColors:
    """StirlingLoggerColors is a class that contains all of the colors that can be used by the StirlingLogger."""

    HEADER = fg(7) + bg(1)
    TIMESTAMP = fg(18)
    DURATION = fg(8)

    INFO = fg(2)
    WARNING = fg(3)
    ERROR = fg(9)
    DEBUG = fg(11)
    RESET = attr(0)

class StirlingLoggerLevel(int, Enum):
    """StirlingLoggerLevel is a class that contains all of the levels that can be used by the StirlingLogger."""

    QUIET = 0
    ERROR = 1
    WARNING = 2
    INFO = 3
    DEBUG = 4


@dataclass
class StirlingLogger(StirlingClass):
    log_file: Path
    time_start: datetime = field(default_factory=datetime.now)
    log_level: StirlingLoggerLevel | None = StirlingLoggerLevel.INFO

    @staticmethod
    def _log_string(
        msg: str, line_identifier: str = "+", indent: int = 4
    ) -> str:
        """Log a string to the job log file."""

        new_line_string = "\n" + line_identifier + " " * indent
        return new_line_string + new_line_string.join(msg.splitlines())

    def _log_object(
        self, obj, prefix: str = "+", header: str = "", indent: int = 4
    ) -> str:
        """Log an object to the job log file.

        Args:
            obj: The object to log
            prefix (str): The prefix to use for each line
            header (str): A header to print before each line
            indent (int): The number of spaces to indent each line of JSON

        Returns:
            str: The object as a string for loggingb
        """
        return self._log_string(
            header + dumps(obj, indent=indent, cls=StirlingJSONEncoder),
            prefix,
            indent,
        )

    def log(self, message: str, *args) -> None:
        """Generic log function that defaults to info level."""
        return self.info(message, *args)

    def info(self, message: str, *args) -> None:
        return self._logger(message, StirlingLoggerLevel.INFO, *args)

    def warn(self, message: str, *args) -> None:
        return self._logger(message, StirlingLoggerLevel.WARNING, *args)

    def error(self, message: str, *args) -> None:
        return self._logger(message, StirlingLoggerLevel.ERROR, *args)

    def debug(self, message: str, *args) -> None:
        return self._logger(message, StirlingLoggerLevel.DEBUG, *args)

    def _logger(self, message: str,  level = StirlingLoggerLevel.INFO, *args) -> None:
        """Write a message to the log file.

        Args:
            message (str): The message to write to the log file.
            level (StirlingLoggerLevel): The level of the message.
            *args (object): Any additional objects to log to the file (as JSON).
        """

        stamp = datetime.now() - self.time_start
        line_header = f"[{bg(239)}{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}{attr(0)}] "
        line_header += f"[{fg(8)}+{str(stamp)}{attr(0)}] "
        line_header += f"[{bg(15)}{self.job_id}{attr(0)}] "
        line_header = f"{line_header}"

        obj_log = "".join(
            self._log_string(object_to_log)
            if isinstance(object_to_log, str)
            else "" # self._log_object(object_to_log)
            for object_to_log in args
        )

        if self.log_level <= self.log_level:
            print(f"{line_header}: {message}{obj_log}")

        try:
            with open(
                file=self.log_file, mode="a", encoding="utf-8"
            ) as log_file_object:
                log_file_object.write(f"{line_header}: {message}")

                # If we have any objects to log, log them
                for line in obj_log.split("\n"):
                    # We're looping here in case we want to prettify each line
                    # (like above) in the future.
                    log_file_object.write(line + "\n")

        except OSError as exc:
            raise FileNotFoundError(
                f"can't access the log file: {self.log_file}, \
                    stopping execution for job {str(self.job_id)}"
            ) from exc

@dataclass
class StirlingJobLogger(StirlingClass):
    job_id: UUID
    log_file: Path
    time_start: datetime = field(default_factory=datetime.now)
    log_level: StirlingLoggerLevel | None = StirlingLoggerLevel.INFO

    @staticmethod
    def _log_string(
        msg: str, line_identifier: str = "+", indent: int = 4
    ) -> str:
        """Log a string to the job log file."""

        new_line_string = "\n" + line_identifier + " " * indent
        return new_line_string + new_line_string.join(msg.splitlines())

    def _log_object(
        self, obj, prefix: str = "+", header: str = "", indent: int = 4
    ) -> str:
        """Log an object to the job log file.

        Args:
            obj: The object to log
            prefix (str): The prefix to use for each line
            header (str): A header to print before each line
            indent (int): The number of spaces to indent each line of JSON

        Returns:
            str: The object as a string for loggingb
        """
        return self._log_string(
            header + dumps(obj, indent=indent, cls=StirlingJSONEncoder),
            prefix,
            indent,
        )

    def log(self, message: str, *args) -> None:
        """Generic log function that defaults to info level."""
        return self.info(message, *args)

    def info(self, message: str, *args) -> None:
        return self._logger(message, StirlingLoggerLevel.INFO, *args)

    def warn(self, message: str, *args) -> None:
        return self._logger(message, StirlingLoggerLevel.WARNING, *args)

    def error(self, message: str, *args) -> None:
        return self._logger(message, StirlingLoggerLevel.ERROR, *args)

    def debug(self, message: str, *args) -> None:
        return self._logger(message, StirlingLoggerLevel.DEBUG, *args)

    def _logger(self, message: str,  level = StirlingLoggerLevel.INFO, *args) -> None:
        """Write a message to the log file.

        Args:
            message (str): The message to write to the log file.
            level (StirlingLoggerLevel): The level of the message.
            *args (object): Any additional objects to log to the file (as JSON).
        """

        stamp = datetime.now() - self.time_start
        line_header = f"[{bg(239)}{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}{attr(0)}] "
        line_header += f"[{fg(8)}+{str(stamp)}{attr(0)}] "
        line_header += f"[{bg(15)}{self.job_id}{attr(0)}] "
        line_header = f"{line_header}"

        obj_log = "".join(
            self._log_string(object_to_log)
            if isinstance(object_to_log, str)
            else "" # self._log_object(object_to_log)
            for object_to_log in args
        )

        if self.log_level <= self.log_level:
            print(f"{line_header}: {message}{obj_log}")

        try:
            with open(
                file=self.log_file, mode="a", encoding="utf-8"
            ) as log_file_object:
                log_file_object.write(f"{line_header}: {message}")

                # If we have any objects to log, log them
                for line in obj_log.split("\n"):
                    # We're looping here in case we want to prettify each line
                    # (like above) in the future.
                    log_file_object.write(line + "\n")

        except OSError as exc:
            raise FileNotFoundError(
                f"can't access the log file: {self.log_file}, \
                    stopping execution for job {str(self.job_id)}"
            ) from exc
