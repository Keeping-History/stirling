import re

from semver import VersionInfo

from stirling.dependencies import StirlingDependency
from stirling.frameworks.ffmpeg.command import (
    StirlingMediaFrameworkFFMpegCommand,
)


def check_ffmpeg_version(transcoder: StirlingDependency, version: str):
    """Verifies the FFMpeg version matches the expected version.

    We accept any version of FFMpeg that is the same major and minor version as the expected version.
    """
    options = {
        "version": True,
    }
    cmd_output = StirlingMediaFrameworkFFMpegCommand(
        binary_dependency=transcoder,
        arguments=None,
        options=options,
    ).run()

    version_find = re.findall(r"(?<=version\s)\S+", cmd_output.splitlines()[0])

    if len(version_find) == 0:
        raise ValueError("Unable to get version of FFMpeg.")

    version_found = version_find[0]

    if len(version_found) == 3:
        version_found = f"{version_found}.0"

    got_version = VersionInfo.parse(version_found)

    if got_version.match(version) is False:
        # TODO: Need a custom error here.
        raise ValueError(
            "FFMpeg version {got_version} does not match the expected version {self.options.version}."
        )
