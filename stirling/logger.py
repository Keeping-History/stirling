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

    HEADER = bg(8) + fg(0)
    TIMESTAMP = fg(18)
    DURATION = fg(8)

    ERROR = bg(9) + fg(0)
    WARNING = bg(3) + fg(0)
    INFO = fg(2)
    DEBUG = fg(11)
    RESET = attr(0)


class StirlingLoggerLevel(int, Enum):
    """StirlingLoggerLevel is a class that contains all of the levels that can be used by the StirlingLogger."""

    QUIET = 0
    CRITICAL = 1
    ERROR = 2
    WARNING = 3
    INFO = 4
    DEBUG = 5


@dataclass
class StirlingLogger(StirlingClass):
    log_file: Path
    log_level: StirlingLoggerLevel | int | None = StirlingLoggerLevel.QUIET
    time_start: datetime = datetime.now()
    header_separator: str = "|"
    line_continuation_prefix: str = "+"

    def _headers(self):
        return [self._date_line_header, self._duration_line_header]

    def log(self, message: str, *args) -> None:
        """Generic log function that defaults to info level."""
        return self.info(message, *args)

    def error(self, message: str, *args) -> None:
        return self._logger(message, StirlingLoggerLevel.ERROR, *args)

    def warn(self, message: str, *args) -> None:
        return self._logger(message, StirlingLoggerLevel.WARNING, *args)

    def info(self, message: str, *args) -> None:
        return self._logger(message, StirlingLoggerLevel.INFO, *args)

    def debug(self, message: str, *args) -> None:
        return self._logger(message, StirlingLoggerLevel.DEBUG, *args)

    def _date_line_header(self):
        return f"{StirlingLoggerColors.HEADER}{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}{StirlingLoggerColors.RESET}"

    def _duration_line_header(self):
        return f"{fg(8)}+{str(datetime.now() - self.time_start)}{attr(0)}"

    @staticmethod
    def _log_string(
        msg: str,
        line_identifier: str = line_continuation_prefix,
        indent: int = 4,
    ) -> str:
        """Log a string."""

        new_line_string = "\n" + line_identifier + " " * indent
        return new_line_string + new_line_string.join(msg.splitlines())

    def _log_object(
        self, obj, prefix: str | None = None, header: str = "", indent: int = 4
    ) -> str:
        """Log an object.

        Args:
            obj: The object to log.
            prefix (str): The prefix to use for each line.
            header (str): A header to print before each line.
            indent (int): The number of spaces to indent each line of JSON.

        Returns:
            str: The object as a string for logging.
        """
        return self._log_string(
            header + dumps(obj, indent=indent, cls=StirlingJSONEncoder),
            prefix or self.line_continuation_prefix,
            indent,
        )

    def _logger(
        self, message: str, level=StirlingLoggerLevel.INFO, *args
    ) -> None:
        """Write a message to the log file.

        Args:
            message (str): The message to write to the log file.
            level (StirlingLoggerLevel): The level of the message.
            *args (object): Any additional objects to log to the file (as JSON).
        """

        if self.log_level >= level:
            obj_log = "".join(
                self._log_string(object_to_log)
                if isinstance(object_to_log, str)
                else self._log_object(object_to_log)
                for object_to_log in args
            )

            lines = [header() for header in self._headers()] + [
                level.name,
                f"{message}{obj_log}",
            ]

            log_line = f" {self.header_separator} ".join(lines)

            print(log_line)

            try:
                with open(
                    file=self.log_file, mode="a", encoding="utf-8"
                ) as log_file_object:
                    log_file_object.write(f"{log_line}")

                    # If we have any objects to log, log them
                    for line in obj_log.split("\n"):
                        # We're looping here in case we want to prettify each line
                        # (like above) in the future.
                        log_file_object.write(line + "\n")

            except OSError as exc:
                raise FileNotFoundError(
                    f"can't access the log file: {self.log_file}, \
                        stopping execution."
                ) from exc


@dataclass
class StirlingJobLogger(StirlingLogger):
    job_id: UUID | None = None

    def _headers(self):
        return [
            self._date_line_header,
            self._duration_line_header,
            self._job_id_header,
        ]

    def _job_id_header(self):
        return f"{StirlingLoggerColors.HEADER}{self.job_id}{StirlingLoggerColors.RESET}"
