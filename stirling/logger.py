from dataclasses import field
from datetime import datetime
from json import dumps
from pathlib import Path
from uuid import UUID

from pydantic.dataclasses import dataclass

from stirling.core import StirlingClass
from stirling.encodings import StirlingJSONEncoder


@dataclass
class StirlingLogger(StirlingClass):
    job_id: UUID
    log_file: Path
    time_start: datetime = field(default_factory=datetime.now)
    debug: bool = False

    @staticmethod
    def log_string(
        msg: str, line_identifier: str = "+", indent: int = 4
    ) -> str:
        """Log a string to the job log file."""

        new_line_string = "\n" + line_identifier + " " * indent
        return new_line_string + new_line_string.join(msg.splitlines())

    def log_object(
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

        return self.log_string(
            header + dumps(obj, indent=indent, cls=StirlingJSONEncoder),
            prefix,
            indent,
        )

    def log(self, message: str, *args) -> None:
        """Write a message to the log file.

        Args:
            message (str): The message to write to the log file.
            *args (object): Any additional objects to log to the file (as JSON).
        """

        stamp = datetime.now() - self.time_start
        line_header = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}] [+{str(stamp)}] [{self.job_id}]"

        obj_log = "".join(
            self.log_string(object_to_log)
            if isinstance(object_to_log, str)
            else self.log_object(object_to_log)
            for object_to_log in args
        )
        if self.debug:
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
