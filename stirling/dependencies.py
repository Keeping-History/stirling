import os
import platform
import shutil
import tarfile
from dataclasses import field
from enum import auto
from io import BytesIO, TextIOWrapper
from pathlib import Path
from typing import List, Tuple, Union
from uuid import uuid4
from zipfile import ZipFile

from dataclasses_json import dataclass_json
from pydantic.dataclasses import dataclass
from requests import get as get_url
from requests.exceptions import RequestException
from strenum import LowercaseStrEnum

from stirling.core import StirlingClass
from stirling.errors import (
    DependencyMissingBinaryError,
    DependencyMissingDownloadError,
    DependencyMissingPostProcessError,
)


class StirlingDependencyPostActions(LowercaseStrEnum):
    """StirlingDependencyPostActions is a list of post actions that can be taken after downloading a dependency."""

    UNZIP = auto()
    UNTAR = auto()
    TXT = auto()
    BIN = auto()


@dataclass_json
@dataclass
class StirlingDependency(StirlingClass):
    """StirlingDependency is the class for all Stirling dependencies.

    This class adds helper functions for all binary dependencies that will
    be used.

    Attributes:
        name (Union[str, Path]): A name to be referred to by other functions
            intending to use the dependency.
        binary (Union[str, Path]): The name of the binary file (available in
            the PATH), the name of the binary that will be extracted from a
            downlaoded package, or the full path to the binary.
        version (str): The version of the binary to use.
        platform (Tuple[str, str]): The platform and architecture of the
            binary to use (e.g. ("darwin", "amd64")).
        url (str | None): The URL to download the binary from.
        post_process (StirlingDependencyPostActions | None): The post
            process action to take after downloading the file from the URL.
            These actions can include things like downloading the file directly,
            building an executable from source or decompressing the downloaded
            file.
        force_download (bool | None): Force the download of the binary.
            This will overwrite any files.json in the ./bin/ directory that have the
            ame name.
        move_all (bool | None): Move all files.json in the archive to the ./bin/
            directory. This is useful when an archive contains libraries or
            other additional files.json needed to run, besides the executable itself.


    Typical usage example:

        Download a binary dependency and save it to the ./bin/ directory.
        >>> from stirling.dependencies import StirlingDependency, \
        ...     StirlingDependencyPostActions
        >>> ffmpeg = StirlingDependency(
        ...     name="ffmpeg",
        ...     binary="ffmpeg",
        ...     version="6.0.0",
        ...     platform=("darwin", "amd64"),
        ...     url="https://www.osxexperts.net/ffmpeg6intel.zip",
        ...     post_process=StirlingDependencyPostActions.UNTAR,
        ...     force_download=True,
        ...     move_all=False,
        ... )
        >>> ffmpeg.binary # Path(./bin/ffmpeg)
    """

    name: str | Path
    binary: str | Path
    version: str
    platform: Tuple[str, str]
    url: str | None = None
    post_process: StirlingDependencyPostActions | None = None
    force_download: bool | None = False
    move_all: bool | None = False

    def __post_init__(self):
        """Check if the required binary is available."""

        self.bin_directory: Path = Path(Path(os.getcwd()) / "bin").resolve()
        if not os.path.exists(self.bin_directory):
            os.mkdir(self.bin_directory)

        # Check to see if we can find the binary file.
        bin_full_path = self._find_binary()

        if not bin_full_path and self.url:
            # We didn't find the binary as it was passed, it wasn't in the bin/ directory,
            # and we didn't find it in the PATH. Let's download it, if a URL was provided.
            bin_full_path = self._process_binary_package(self._download_binary())

        # Check to see if we were able to find an absolute path to the executable,
        # verify it exists and has the appropriate permissions to run. If any of
        # these checks fail, we will raise an error.
        if not (
            bin_full_path
            and Path(bin_full_path).is_file()
            and os.access(bin_full_path, os.X_OK)
        ):
            raise DependencyMissingBinaryError(
                f"Binary at {bin_full_path} is not found, or is not an executable."
            )

        # If we got this far, we have a valid binary. Let's set the binary to the full path.
        self.binary = bin_full_path

    def _find_binary(self) -> Path | None:
        """Try to find a full Path to the binary."""

        if str(self.binary).startswith(("./", "/")):
            # If the binary is a relative or full path, we will use that one.
            return Path(self.binary).resolve()
        elif self._is_binary_cached():
            # The binary was not a full path, but we found it in the bin/ directory.
            return Path(self.bin_directory / self.binary)
        elif self.force_download is False:
            # We didn't find the binary in the ./bin/ directory. Let's try to find it in the PATH.
            which_ffmpeg = shutil.which(self.binary)
            return Path(which_ffmpeg) if which_ffmpeg else None

        return None

    def _is_binary_cached(self) -> bool:
        """Check if the binary is cached."""
        # Check to see if we have a ./bin directory

        return os.path.exists(self.bin_directory / self.binary) and self.force_download

    def _download_binary(self) -> BytesIO:
        """Download the binary from the URL provided."""

        try:
            response = get_url(str(self.url), timeout=10)
        except RequestException as err:
            raise DependencyMissingDownloadError(
                f"Error downloading {self.url}: {err}"
            ) from err

        if response.status_code != 200:
            raise DependencyMissingDownloadError(
                f"Error downloading {self.url}: Response Code: {response.status_code}"
            )
        return BytesIO(response.content)

    def _process_binary_package(self, stream: BytesIO) -> Path:
        """Process the binary package.

        These include actions like unzipping, untarring, building, running a Docker container
        and capturing its output, and so on.

        The stream is the binary package, which is a BytesIO object.
        """

        handler_func = {
            StirlingDependencyPostActions.UNZIP: self._unzip_stream,
            StirlingDependencyPostActions.UNTAR: self._untar_stream,
            StirlingDependencyPostActions.BIN: self._save_binary_stream,
            StirlingDependencyPostActions.TXT: self._save_text_stream,
        }

        if self.post_process not in handler_func:
            raise DependencyMissingPostProcessError(
                f"Post process {self.post_process} is not supported."
            )

        temp_directory = Path(os.getcwd()) / "tmp" / str(uuid4())
        temp_directory.mkdir(parents=True, exist_ok=True)

        location = handler_func[self.post_process](stream, temp_directory, self.binary)

        try:
            if self.move_all:
                os.rename(location, self.bin_directory / self.binary)
                self.bin_directory = self.bin_directory / self.binary
                self.binary = self.bin_directory / self.binary
            else:
                shutil.copy(location, self.bin_directory / self.binary)

            os.chmod(self.bin_directory / self.binary, 0o755)
            shutil.rmtree(temp_directory)

        except Exception as err:
            raise DependencyMissingDownloadError(
                f"Error downloading {self.binary}: {err}"
            ) from err

        return Path(self.bin_directory / self.binary)

    @staticmethod
    def _unzip_stream(stream: BytesIO, location: Path, binary: str) -> Path:
        """Unzip a bytes stream."""

        with ZipFile(file=stream) as zf:
            zf.extractall(location)
        return location / binary

    @staticmethod
    def _untar_stream(stream: BytesIO, location: Path, binary: str) -> Path:
        """Untar a bytes stream."""

        with tarfile.open(fileobj=stream) as tf:
            tf.extractall(path=location)
        return location / binary

    @staticmethod
    def _save_binary_stream(stream: BytesIO, location: Path, binary: str) -> Path:
        """Save a bytes stream to a binary file."""

        location_output = Path(location / "output")
        with open(location_output, "wb") as bin_file:
            # Write the bytes to a file.
            bin_file.write(stream.read())
        return location_output

    @staticmethod
    def _save_text_stream(stream: BytesIO, location: Path, binary: str) -> Path:
        """Save and re-encode a bytes stream to a text file."""

        location_output = Path(location / "output")
        with open(location_output, "wt") as txt_file:
            # Write the byte data, converted to utf-8 text, to a file.
            txt_file.write(TextIOWrapper(stream, encoding="utf-8").read())
        return location_output


@dataclass_json
@dataclass
class StirlingDependencies(StirlingClass):
    dependencies: List[StirlingDependency] = field(default_factory=list)

    def get(
        self, name: str, system_os: str = None, system_arch: str = None
    ) -> StirlingDependency:
        """Get the dependencies for a given platform."""
        system_os = system_os or platform.system()
        system_arch = system_arch or platform.machine()

        dependency = [
            dependency
            for dependency in self.dependencies
            if dependency.name == name
            and dependency.platform == (system_os, system_arch)
        ]

        return next(iter(dependency), None)

    def add_dep(self, dep: StirlingDependency):
        self.dependencies.append(dep)
