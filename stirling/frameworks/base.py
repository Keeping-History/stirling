from dataclasses import field
from pathlib import Path
from typing import List

from pydantic.dataclasses import dataclass

from stirling.core import StirlingClass
from stirling.dependencies import StirlingDependencies
from stirling.frameworks.media_info import (
    StirlingMediaInfo,
    StirlingMediaInfoCodec,
    StirlingMediaInfoContainer,
)


@dataclass(kw_only=True)
class StirlingMediaFrameworkCapabilities(StirlingClass):
    """The capabilities of the framework."""

    codecs: List[StirlingMediaInfoCodec] = None
    containers: List[StirlingMediaInfoContainer] = None


@dataclass
class StirlingMediaFrameworkOptions(StirlingClass):
    """Specify which version os the Media Framework to support.

    Version should be true semantic version or version match string.
    """

    version: str


@dataclass
class StirlingMediaFramework(StirlingClass):
    """StirlingMediaFramework is a class for handling the underlying system
    media framework used to interact with media files.


    Args:
        name (str): The encoder framework to use. For example, `FFMpeg` is a
            media framework that can be used to interact with media
            files; `Mencoder` and `MLT` are other examples of media frameworks.
    """

    name: str
    options: StirlingMediaFrameworkOptions | None = None
    dependencies: StirlingDependencies = field(default_factory=list)
    capabilities: StirlingMediaFrameworkCapabilities = field(
        default_factory=StirlingMediaFrameworkCapabilities
    )

    def probe(self, source: str | Path) -> StirlingMediaInfo:
        """Probe the source file and return a StirlingMediaInfo object."""
        ...
