import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from stirling.codecs.video.base import StirlingMediaCodecVideoBase
from stirling.codecs.base import get_codec
from stirling.command.base import StirlingCommand
from stirling.config import StirlingConfig
from stirling.containers.base import StirlingMediaContainer, get_container
from stirling.job import StirlingJob
from stirling.plugins.core import StirlingPlugin, StirlingPluginOptions


class StirlingPluginVideoOptions(StirlingPluginOptions):
    plugin_name: str = "video"
    codec: str | StirlingMediaCodecVideoBase = None
    container: str | StirlingMediaContainer = None
    output_directory: Path | str | None = None
    filename: str | None = None
    start_time: float | None = None
    end_time: float | None = None


def get_plugin():
    return StirlingPluginVideo


@dataclass(kw_only=True)
class StirlingPluginVideo(StirlingPlugin):
    """StirlingPluginVideo extracts the video from a source file."""

    name: str = "video"
    depends_on = None
    options: StirlingPluginVideoOptions | str | dict | None = None

    def __post_init__(self):
        self._counter: int = 0

        self.logger.debug(f"Initializing plugin {self.name}")
        self.options: StirlingPluginVideoOptions = (
            StirlingPluginVideoOptions.parse_options(self.options)
        )

        if type(self.options.codec) is str:
            self.options.codec = get_codec(self.options.codec)

        if type(self.options.container) is str:
            self.options.container = get_container(self.options.container)

    def cmds(self, job: StirlingJob):
        """Extract video from a media file."""
        self._counter += 1

        return [
            StirlingCommand(
                name=f"{self.name}_{self._counter}",
                dependency=job.framework.options.dependencies.get(job.framework.name),
                expected_outputs=[self._cmd_output(job, self._counter)],
            )
        ]

    def _cmd_output(self, job: StirlingJob, counter: int):
        return Path(
            job.options.output_directory.resolve()
            / f"{self.name}_{str(counter)}-{self.options.codec.output_name}.{self.options.container.file_extension}"
        )
