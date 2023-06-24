"""
core.py

This file contains the StirlingMediaFrameworkFFMpeg class, which is a class
for using the `ffmpeg` Media Framework.

The StirlingMediaFrameworkFFMpeg class inherits from the
StirlingMediaFramework class.

"""
import os
from dataclasses import field
from pathlib import Path
from typing import Dict, Tuple, Union

from multipledispatch import dispatch
from pydantic.dataclasses import dataclass

from stirling.core import StirlingClass
from stirling.dependencies import StirlingDependencies, StirlingDependency
from stirling.frameworks.base import (
    StirlingMediaFramework,
    StirlingMediaFrameworkCapabilities,
    StirlingMediaFrameworkOptions,
)
from stirling.frameworks.ffmpeg.codecs import StirlingMediaInfoCodecParser
from stirling.frameworks.ffmpeg.containers import (
    StirlingMediaInfoContainerParser,
)
from stirling.frameworks.ffmpeg.helpers import get_video_letterbox_detect
from stirling.frameworks.ffmpeg.operations.crop import (
    crop_ratio,
    crop_ratio_x_y,
    crop_w_h_x_y,
)
from stirling.frameworks.ffmpeg.operations.resize import (
    resize_ratio,
    resize_w_h,
)
from stirling.frameworks.ffmpeg.operations.trim import trim_start_end
from stirling.frameworks.ffmpeg.probe import StirlingMediaFrameworkFFMpegProbe
from stirling.frameworks.ffmpeg.version import check_ffmpeg_version
from stirling.frameworks.media_info import (
    StirlingMediaInfo,
    StirlingStreamAudio,
    StirlingStreamText,
    StirlingStreamVideo,
)


class StirlingMediaFrameworkFFMpegClass(StirlingClass):
    pass


@dataclass
class StirlingMediaFrameworkFFMpegOptions(StirlingMediaFrameworkOptions):
    version: str = ">=6.0.0"
    binary_transcoder: str = "ffmpeg"
    binary_probe: str = "ffprobe"


@dataclass(kw_only=True)
class StirlingMediaFrameworkFFMpeg(StirlingMediaFramework):
    """StirlingMediaFrameworkFFMpeg is a class for using the `ffmpeg` Media
    Framework to interact with media files
    and their metadata.

    When using any version of `ffmpeg`, please note: it is required to pass
    additional arguments to `ffmpeg`
    at the time the static binary is built to enable support for some
    specific media libraries and codecs.
    You can check the supported codecs and containers by using the
    capabilities property.
    """

    name: str = "FFMpeg"
    options: StirlingMediaFrameworkFFMpegOptions = field(
        default_factory=StirlingMediaFrameworkFFMpegOptions
    )

    def __post_init__(self):
        # Check to make sure the appropriate binary files we need are installed.

        self._binary_transcoder: StirlingDependency
        self._binary_probe: StirlingDependency

        self._default_cmd_options: dict = {}

        with open(
            f"{os.getcwd()}/configs/frameworks/{self.name.lower()}.json", "r"
        ) as f:
            self.dependencies = StirlingDependencies.from_json(f.read())

        self._binary_transcoder = self.dependencies.get(
            self.options.binary_transcoder
        )
        self._binary_probe = self.dependencies.get(self.options.binary_probe)

        check_ffmpeg_version(self._binary_transcoder, self.options.version)

        self.capabilities = StirlingMediaFrameworkCapabilities(
            codecs=StirlingMediaInfoCodecParser(self._binary_transcoder).get(),
            containers=StirlingMediaInfoContainerParser(
                self._binary_transcoder
            ).get(),
        )

    def probe(self, source: str | Path) -> StirlingMediaInfo:
        return StirlingMediaFrameworkFFMpegProbe(
            source,
            self._default_cmd_options,
            self._binary_transcoder,
            self._binary_probe,
        ).probe()

    @dispatch(int, int, StirlingStreamVideo)
    def resize(
        self, width: int, height: int, stream: StirlingStreamVideo
    ) -> Dict[str, str]:
        """Resize the video to a specific width and height."""
        return resize_w_h(width, height)

    @dispatch(tuple, StirlingStreamVideo)
    def resize(
        self, ratio: Tuple[int, int], stream: StirlingStreamVideo
    ) -> Dict[str, str]:
        """Resize the video to a specific scale/ratio."""
        return resize_ratio(ratio)

    @dispatch(int, int, StirlingStreamVideo)
    def scale(
        self, width: int, height: int, stream: StirlingStreamVideo
    ) -> Dict[str, str]:
        """Scale is an alias for resize."""
        return self.resize(width, height, stream)

    @dispatch(tuple, StirlingStreamVideo)
    def scale(
        self, ratio: Tuple[int, int], stream: StirlingStreamVideo
    ) -> Dict[str, str]:
        """Scale is an alias for resize."""
        return self.resize(ratio, stream)

    @dispatch(int, int, int, int, StirlingStreamVideo)
    def crop(
        self,
        width: int,
        height: int,
        start_x: int,
        start_y: int,
        stream: StirlingStreamVideo,
    ) -> Dict[str, str]:
        """Crop the video to a specific width, height, and starting position."""
        return crop_w_h_x_y(width, height, start_x, start_y)

    @dispatch(tuple, StirlingStreamVideo)
    def crop(
        self, ratio: Tuple[int, int], stream: StirlingStreamVideo
    ) -> Dict[str, str]:
        """Crop the video to a specific ratio/scale."""
        return crop_ratio(ratio)

    @dispatch(tuple, tuple, StirlingStreamVideo)
    def crop(
        self,
        ratio: Tuple[int, int],
        position: Tuple[int, int],
        stream: StirlingStreamVideo,
    ) -> Dict[str, str]:
        """Crop the video to a specific ratio/scale, with a starting
        position."""
        return crop_ratio_x_y(ratio, position)

    @dispatch(Path, StirlingStreamVideo)
    def crop(self, source: Path, stream: StirlingStreamVideo) -> Dict[str, str]:
        """Crop the video using the black-bar auto-detection feature of
        FFMpeg."""
        box = get_video_letterbox_detect(
            self._binary_transcoder,
            self._binary_probe,
            source,
            stream.stream_id,
            self._default_cmd_options,
        )

        return crop_w_h_x_y(*box)

    @dispatch(
        (str, int, float),
        (str, int, float),
        [(StirlingStreamVideo, StirlingStreamAudio)],
    )
    def trim(
        self,
        time_start: str | int | float,
        time_end: str | int | float,
        stream: Union[StirlingStreamVideo, StirlingStreamAudio],
    ) -> Dict[str, str]:
        """Trim the video to a specific start and end time."""
        return trim_start_end(time_start, time_end)

    @dispatch((str, int, float), (str, int, float), StirlingStreamText)
    def trim(
        self,
        stream: StirlingStreamText,
        time_start: str | int | float,
        time_end: str | int | float,
    ) -> Dict[str, str]:
        raise NotImplementedError(
            "Trimming is not supported for this stream type."
        )
