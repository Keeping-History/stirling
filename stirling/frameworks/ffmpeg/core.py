"""
base.py

This file contains the StirlingMediaFrameworkFFMpeg class, which is a class
for using the `ffmpeg` Media Framework.

The StirlingMediaFrameworkFFMpeg class inherits from the
StirlingMediaFramework class.

"""

from pathlib import Path
from typing import Dict, Tuple, Union

from multipledispatch import dispatch
from pydantic.dataclasses import dataclass

from stirling.codecs.base import get_codec
from stirling.config import StirlingConfig
from stirling.containers.base import get_container
from stirling.dependencies import StirlingDependency, StirlingDependencies
from stirling.frameworks.base import (
    StirlingMediaFramework,
    StirlingMediaFrameworkCapabilities,
    StirlingMediaFrameworkOptions,
)
from stirling.frameworks.base import (
    StirlingMediaInfo,
    StirlingStreamAudio,
    StirlingStreamText,
    StirlingStreamVideo,
)
from stirling.frameworks.ffmpeg.codecs.base import StirlingFFMpegCodecParser
from stirling.frameworks.ffmpeg.containers.base import (
    StirlingFFMpegContainerParser,
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
from stirling.logger import get_job_logger

ffmpeg_framework_global = None


def get_ffmpeg_framework(
    version: str | None = None,
    binary_transcoder: str | None = None,
    binary_probe: str | None = None,
    dependencies: StirlingDependencies | None = None,
    default_cmd_options: dict | None = None,
    use_cached: bool = True,
) -> "StirlingMediaFrameworkFFMpeg":
    """Get the FFMpeg framework."""

    global ffmpeg_framework_global
    if ffmpeg_framework_global is None or use_cached is False:
        ffmpeg_framework_global = StirlingMediaFrameworkFFMpeg(
            version, binary_transcoder, binary_probe, dependencies, default_cmd_options
        )
    return ffmpeg_framework_global


@dataclass
class StirlingMediaFrameworkFFMpegOptions(StirlingMediaFrameworkOptions):
    version: str = None
    binary_transcoder: str = None
    binary_probe: str = None
    dependencies: StirlingDependencies | None = None
    default_cmd_options: dict | None = None

    def __post_init__(self):
        default_options = StirlingConfig().get("frameworks/ffmpeg/options")
        self.version = self.version or default_options.get("version")
        self.binary_transcoder = self.binary_transcoder or default_options.get(
            "binary_transcoder"
        )
        self.binary_probe = self.binary_probe or default_options.get("binary_probe")
        self.default_cmd_options = self.default_cmd_options or default_options.get(
            "default_cmd_options"
        )
        if self.dependencies is None:
            self.dependencies = StirlingDependencies()
            for dependency in default_options.get("dependencies"):
                self.dependencies.add_dep(dep=StirlingDependency.from_dict(dependency))


@dataclass(kw_only=True)
class StirlingMediaFrameworkFFMpeg(StirlingMediaFramework):
    """StirlingMediaFrameworkFFMpeg is a class for using the `ffmpeg` Media
    Framework to interact with media files.json
    and their metadata.

    When using any version of `ffmpeg`, please note: it is required to pass
    additional arguments to `ffmpeg`
    at the time the static binary is built to enable support for some
    specific media libraries and codecs.
    You can check the supported codecs and containers by using the
    capabilities property.
    """

    name: str = "ffmpeg"
    options: StirlingMediaFrameworkFFMpegOptions | None = None

    def __post_init__(self):
        self.logger = get_job_logger()

        self.logger.info("FFMpeg Framework loading.")

        self.options = self.options or StirlingMediaFrameworkFFMpegOptions()

        self._binary_transcoder = self.options.dependencies.get(
            self.options.binary_transcoder
        )
        self._binary_probe = self.options.dependencies.get(self.options.binary_probe)

        check_ffmpeg_version(self._binary_transcoder, self.options.version)

        self.capabilities = StirlingMediaFrameworkCapabilities(
            codecs=StirlingFFMpegCodecParser(self._binary_transcoder).get(),
            containers=StirlingFFMpegContainerParser(self._binary_transcoder).get(),
        )

        self.logger.info("FFMpeg Framework loaded.")

    def probe(self, source: str | Path) -> StirlingMediaInfo:
        return StirlingMediaFrameworkFFMpegProbe(
            source,
            self._binary_transcoder,
            self._binary_probe,
            self.options.default_cmd_options,
        ).probe()

    def codec_container_supported(
        self, codec_name: str, container_extension: str
    ) -> bool:
        """Check if the codec and container are supported."""

        codec_to_check = get_codec(codec_name)
        container_to_check = get_container(container_extension)

        # TODO: Currently, we don't have a table of supported codecs to containers.
        # For now, just return True.
        return True

    def get_dependency(self, name: str | None = None) -> StirlingDependency:
        match name:
            case "binary_probe":
                return self._binary_probe
            case _:
                return self._binary_transcoder

    def get_codec(self, codec_name: str):
        return [cdict for cdict in self.capabilities.codecs if cdict.name == codec_name]

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
            self.options.default_cmd_options,
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
        time_start: str | int | float,
        time_end: str | int | float,
        stream: StirlingStreamText,
    ) -> Dict[str, str]:
        raise NotImplementedError("Trimming is not supported for this stream type.")
