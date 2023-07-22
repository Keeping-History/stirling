import subprocess
from typing import List

from pydantic.dataclasses import dataclass

from stirling.core import StirlingClass
from stirling.dependencies import StirlingDependency
from stirling.frameworks.ffmpeg.parser import get_probe_unparser


@dataclass(kw_only=True)
class StirlingMediaFrameworkFFMpegCommand(StirlingClass):
    """StirlingMediaFrameworkFFMpegCommand is a class that is used to create
    a command for the FFMpeg CLI."""

    dependency: StirlingDependency
    arguments: dict | str | List | None = None
    keyword_arguments: dict | None = None
    options: dict | None = None

    def __post_init__(self):
        default_cmd_options = {}

        self.options = self.options or default_cmd_options
        self.keyword_arguments = (
            {
                **default_cmd_options,
                **self.keyword_arguments,
            }
            if self.keyword_arguments
            else default_cmd_options
        )

    def cmd(self):
        if self.arguments is None:
            return " ".join(
                [
                    str(self.dependency.binary),
                    get_probe_unparser().unparse(
                        **self.keyword_arguments, **self.options
                    ),
                ]
            )

        return " ".join(
            [
                str(self.dependency.binary),
                get_probe_unparser().unparse(
                    *self.arguments, **self.keyword_arguments, **self.options
                ),
            ]
        )

    def run(self) -> str:
        cmd_output = subprocess.getstatusoutput(cmd := self.cmd())

        if cmd_output[0] != 0 or cmd_output[1] == "":
            raise ValueError(f"Unable to get run command: {cmd}: {cmd_output}.")

        return cmd_output[1]
