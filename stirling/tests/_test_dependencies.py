import os
import shutil
from pathlib import Path

import pytest

from stirling.dependencies import (
    StirlingDependencyPostActions,
    StirlingDependencies,
    StirlingDependency,
)

TEST_DEPENDENCIES = """{
  "dependencies": [
    {
      "name": "ffmpeg",
      "binary": "ffmpeg",
      "version": "6.0.0",
      "platform": [
        "Darwin",
        "arm64"
      ],
      "url": "https://www.osxexperts.net/ffmpeg6arm.zip",
      "post_process": "unzip",
      "force_download": true
    },
    {
      "name": "ffmpeg",
      "binary": "ffmpeg",
      "version": "6.0.0",
      "platform": [
        "Darwin",
        "amd64"
      ],
      "url": "https://www.osxexperts.net/ffmpeg6intel.zip",
      "post_process": "unzip",
      "force_download": true
    },
    {
      "name": "ffprobe",
      "binary": "ffprobe",
      "version": "6.0.0",
      "platform": [
        "Darwin",
        "arm64"
      ],
      "url": "https://www.osxexperts.net/ffprobe6arm.zip",
      "post_process": "unzip",
      "force_download": true
    },
    {
      "name": "ffprobe",
      "binary": "ffprobe",
      "version": "6.0.0",
      "platform": [
        "Darwin",
        "amd64"
      ],
      "url": "https://www.osxexperts.net/ffprobe6intel.zip",
      "post_process": "unzip",
      "force_download": true
    }
  ]
}
"""


def clear_bin_directory():
    shutil.rmtree(Path(os.getcwd()) / "bin", ignore_errors=True)
    shutil.rmtree(Path(os.getcwd()) / "tmp", ignore_errors=True)


@pytest.mark.parametrize(
    "data,expected",
    [
        (
            ["ffmpeg", "Darwin", "arm64"],
            StirlingDependency(
                name="ffmpeg",
                binary="ffmpeg",
                version="6.0.0",
                platform=("Darwin", "arm64"),
                url="https://www.osxexperts.net/ffmpeg6arm.zip",
                post_process=StirlingDependencyPostActions.UNZIP,
                force_download=True,
            ),
        ),
        (
            ["ffprobe", "Darwin", "amd64"],
            StirlingDependency(
                name="ffprobe",
                binary="ffprobe",
                version="6.0.0",
                platform=("Darwin", "amd64"),
                url="https://www.osxexperts.net/ffprobe6intel.zip",
                post_process=StirlingDependencyPostActions.UNZIP,
                force_download=True,
            ),
        ),
    ],
)
def test_get_dependency(data: list, expected: dict):
    clear_bin_directory()
    a = StirlingDependencies.from_json(TEST_DEPENDENCIES)
    b = a.get(data[0], data[1], data[2])
    assert b == expected
