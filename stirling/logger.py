from dataclasses import field
from datetime import datetime
from enum import Enum
from json import dumps
from pathlib import Path
from typing import List
from uuid import UUID

from colored import attr, bg, fg
from pydantic.dataclasses import dataclass

from stirling.core import StirlingClass
from stirling.encodings import StirlingJSONEncoder


class StirlingLoggerLevel(int, Enum):
    """StirlingLoggerLevel is a class that contains all levels that can be used by the StirlingLogger."""

    QUIET = 0
    CRITICAL = 1
    ERROR = 2
    WARNING = 3
    INFO = 4
    DEBUG = 5


class StirlingLoggerColors:
    """StirlingLoggerColors is a class that contains the colors that can be used by the StirlingLogger.

    A table of colors is available by running the following command in a terminal window:
    curl -s https://gist.githubusercontent.com/HaleTom/89ffe32783f89f403bba96bd7bcd1263/raw/e50a28ec54188d2413518788de6c6367ffcea4f7/print256colours.sh | bash

    """

    RESET = attr(0)

    DEFAULT = attr(0)

    SEPARATOR = fg(8)
    HEADER = bg(8) + fg(0)
    TIMESTAMP = fg(18)
    DURATION = fg(8)

    CRITICAL = bg(1) + fg(15)
    ERROR = bg(1) + fg(15)
    WARNING = bg(3) + fg(0)
    INFO = bg(12) + fg(0)
    DEBUG = bg(8) + fg(15)

    HIGHLIGHT = bg(0) + fg(12)

    MESSAGE = fg(255)

    OBJECT = fg(8)
    OBJECT_LINE_HEADER = fg(8)

    OBJECT_KEY = fg(40)
    OBJECT_VALUE = fg(228)

    @classmethod
    def _highlight_string(cls, string_to_highlight: str, color: str):
        return "".join([color, string_to_highlight, cls.RESET])

    @classmethod
    def highlight(cls, string_to_highlight: str):
        return cls._highlight_string(string_to_highlight, cls.HIGHLIGHT)

    @classmethod
    def critical(cls, string_to_highlight: str | None = None):
        if string_to_highlight is None:
            string_to_highlight = "CRITICAL"
        return cls._highlight_string(string_to_highlight, cls.CRITICAL)

    @classmethod
    def error(cls, string_to_highlight: str | None = None):
        if string_to_highlight is None:
            string_to_highlight = "ERROR"
        return cls._highlight_string(string_to_highlight, cls.ERROR)

    @classmethod
    def warning(cls, string_to_highlight: str | None = None):
        if string_to_highlight is None:
            string_to_highlight = "WARNING"
        return cls._highlight_string(string_to_highlight, cls.WARNING)

    @classmethod
    def info(cls, string_to_highlight: str | None = None):
        if string_to_highlight is None:
            string_to_highlight = "INFO"
        return cls._highlight_string(string_to_highlight, cls.INFO)

    @classmethod
    def debug(cls, string_to_highlight: str | None = None):
        if string_to_highlight is None:
            string_to_highlight = "DEBUG"
        return cls._highlight_string(string_to_highlight, cls.DEBUG)


@dataclass
class StirlingLogger(StirlingClass):
    log_file: Path = "./stirling.log"
    log_level: StirlingLoggerLevel | int | None = StirlingLoggerLevel.QUIET
    time_start: datetime = datetime.now()
    header_separator: str = " | "
    line_continuation_prefix: str = "+"
    headers: List[str] = field(
        default_factory=lambda: ["timestamp", "duration"]
    )

    def __post_init__(self):
        self._available_headers = {
            "timestamp": self._date_line_header,
            "duration": self._duration_line_header,
        }

    def _headers(self):
        for header in self.headers:
            if header in self._available_headers:
                yield self._available_headers[header]

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

    @staticmethod
    def _date_line_header():
        return "".join(
            [
                StirlingLoggerColors.HEADER,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                StirlingLoggerColors.RESET,
            ]
        )

    def _duration_line_header(self):
        return "".join(
            [fg(8), "+", str(datetime.now() - self.time_start), attr(0)]
        )

    @staticmethod
    def _line_formatter(line: str, level: StirlingLoggerLevel | None) -> str:
        return line

    @staticmethod
    def _log_string(
        msg: str,
        line_identifier: str = line_continuation_prefix,
        indent: int = 4,
    ) -> str:
        """Log a string."""

        new_line_string = "\n" + line_identifier + " " * indent
        return new_line_string + new_line_string.join(msg.splitlines())

    @staticmethod
    def _colorize_json_keys(obj_string):
        if group := obj_string.group():
            return f'"{"".join([StirlingLoggerColors.OBJECT_KEY, group[1:-2], StirlingLoggerColors.RESET])}":'

    @staticmethod
    def _colorize_json_values(obj_string):
        value_header = value_footer = value_end = value_newline = ""

        group = obj_string.group()

        if len(group) < 2:
            return

        if group[-1:] == ",":
            value_end = ","
        else:
            value_newline = "\n"

        msg = group[2:-1]

        if msg[0] == '"' and msg[-1:] == '"':
            value_header, value_footer, msg = '"', '"', group[3:-2]

        json_value_items = [
            value_header,
            StirlingLoggerColors.OBJECT_VALUE,
            msg,
            StirlingLoggerColors.RESET,
            value_footer,
            value_end,
            value_newline,
        ]
        return f": {''.join(json_value_items)}"

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
        import re

        obj_string = dumps(obj, indent=indent, cls=StirlingJSONEncoder)

        results = re.sub(r"\"(.*?)\":", self._colorize_json_keys, obj_string)
        results = re.sub(
            r": \"?(.*?)(,\n)", self._colorize_json_values, results
        )
        results = re.sub(r": ?(.*?)\n", self._colorize_json_values, results)

        return self._log_string(
            header + results,
            StirlingLoggerColors.SEPARATOR
            + (prefix or self.line_continuation_prefix)
            + StirlingLoggerColors.RESET,
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

            log_level_header = (
                getattr(StirlingLoggerColors, level.name)
                or StirlingLoggerColors.DEFAULT
            )

            lines = [header() for header in self._headers()] + [
                log_level_header + level.name + StirlingLoggerColors.RESET,
                f"{message}{obj_log}",
            ]

            log_line = (
                f"{StirlingLoggerColors.DEFAULT}{StirlingLoggerColors.SEPARATOR}{self.header_separator}{StirlingLoggerColors.RESET}".join(
                    lines
                )
                + f"{StirlingLoggerColors.RESET}"
            )

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
                        line = self._line_formatter(line, None)
                        log_file_object.write(line + "\n")

            except OSError as exc:
                raise FileNotFoundError(
                    f"can't access the log file: {self.log_file}, \
                        stopping execution."
                ) from exc


@dataclass
class StirlingJobLogger(StirlingLogger):
    job_id: UUID | None = None
    headers: List[str] = field(
        default_factory=lambda: ["timestamp", "duration", "jobid"]
    )

    def __post_init__(self):
        super().__post_init__()
        self._available_headers.update({"jobid": self._job_id_header})

    def _job_id_header(self):
        return f"{StirlingLoggerColors.HEADER}{self.job_id}{StirlingLoggerColors.RESET}"


job_logger = None


def get_job_logger(
    job_id: UUID = None,
    log_file: Path = None,
    log_level: StirlingLoggerLevel | int = None,
    time_start: datetime = None,
    header_separator: str = None,
    line_continuation_prefix: str = None,
    headers: List[str] = None,
):
    global job_logger

    if not job_logger:
        job_logger_options = {
            "job_id": job_id,
            "log_file": log_file,
            "log_level": log_level,
            "time_start": time_start,
            "header_separator": header_separator,
            "line_continuation_prefix": line_continuation_prefix,
            "headers": headers,
        }

        job_logger = StirlingJobLogger(
            **{k: v for k, v in job_logger_options.items() if v is not None}
        )

    return job_logger
