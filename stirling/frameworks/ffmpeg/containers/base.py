from typing import List, Tuple

from pydantic.dataclasses import dataclass

from stirling.core import StirlingClass
from stirling.dependencies import StirlingDependency
from stirling.frameworks.ffmpeg.command import (
    StirlingMediaFrameworkFFMpegCommand,
)
from stirling.frameworks.base import (
    StirlingMediaInfoContainer,
)


@dataclass
class StirlingFFMpegContainerParser(StirlingClass):
    def __init__(self, binary_transcoder: StirlingDependency):
        self._binary_transcoder = binary_transcoder

    @staticmethod
    def _get_container_actions(row: str) -> Tuple[bool, bool]:
        """Determines if the container can be encoded or decoded to."""
        encode = "E" in row[2]
        decode = "D" in row[1]
        return encode, decode

    @staticmethod
    def _get_container_description(row: str) -> str:
        split_line = row[4:].strip().split(" ", 1)
        return split_line[1].strip() if len(split_line) > 1 else ""

    @staticmethod
    def _get_container_extensions(row: str) -> List[str]:
        """Returns a list of file extensions available for a container."""
        split_line = row[4:].strip().split(" ", 1)
        return split_line[0].split(",")

    def get(self) -> List[StirlingMediaInfoContainer]:
        """A static method that queries FFMpeg and returns a list of available
        codecs.

        Returns:
            List[StirlingMediaInfoContainer]
        """

        """A static method that queries FFMpeg and returns a list of available
        containers types that encoders and decoders can use.

        Returns:
            List[StirlingMediaInfoContainer]
        """
        all_containers = []

        options = {
            "hide_banner": True,
        }

        cmd_output = StirlingMediaFrameworkFFMpegCommand(
            binary_dependency=self._binary_transcoder,
            options=options,
            keyword_arguments={
                "formats": True,
            },
        ).run()

        if cmd_output == "":
            raise ValueError("Unable to get supported containers from FFMpeg.")

        rows = cmd_output[cmd_output.find("--\n") + 3 :].split("\n")
        for row in rows:
            this_container = StirlingMediaInfoContainer(
                description=self._get_container_description(row),
                file_extensions=self._get_container_extensions(row),
            )
            (
                this_container.encode,
                this_container.decode,
            ) = self._get_container_actions(row)
            all_containers.append(this_container)

        return all_containers
