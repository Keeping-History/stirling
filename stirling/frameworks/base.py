from abc import abstractmethod, ABC
from dataclasses import field
from pathlib import Path
from typing import Dict, List, Tuple, Union

from pydantic.dataclasses import dataclass

from stirling.core import StirlingClass
from stirling.dependencies import StirlingDependencies


@dataclass(kw_only=True)
class StirlingStream(StirlingClass):
    """A stream containing encoded information in a container.

    Attributes:
        stream_id (int): the ID of the stream, typically in the order the
            streams are encoded.
        type (str): The type of content in the steam. This must match
            a defined StirlingStreamType. Provided types are video, audio or
            subtitle. Custom types can be defined by plugins.
        duration (float): The duration, in seconds, of the stream.

    """

    stream_id: int
    type: str
    duration: float


@dataclass(kw_only=True)
class StirlingStreamVideo(StirlingStream):
    """The video stream class."""

    width: int
    height: int
    frame_rate: float
    aspect: Tuple
    codec: str

    type: str = "video"

    bit_rate: int | None = None
    profile: str | None = None
    color_model: str | None = None
    scan_type: str | None = None
    version: str | None = None


@dataclass(kw_only=True)
class StirlingStreamAudio(StirlingStream):
    """The audio stream class."""

    channels: int
    bit_rate: str
    sample_rate: int
    codec: str

    type: str = "audio"

    language: str = "und"  # undetermined
    channel_layout: str | None = None
    profile: str | None = None


@dataclass(kw_only=True)
class StirlingStreamText(StirlingStream):
    """The text stream class."""

    start_time: float
    type: str = "subtitle"

    language: str | None = "und"  # undetermined
    dispositions: List[Dict[str, bool]] = field(default_factory=list)


@dataclass
class StirlingMediaInfo(StirlingClass):
    """StirlingMediaInfo is the base class for all media information.

    Attributes:
        source (str): The source file.
        streams (List[StirlingStream]): A list of streams in the source file.
        preferred (Dict): A dictionary of preferred streams for each stream type.
    """

    source: str | Path
    streams: List[StirlingStream] = field(default_factory=list)
    preferred: Dict = field(default_factory=dict)

    def get_stream(self, stream_id: int) -> Union[StirlingStream, None]:
        """Returns a specific stream, specified by its stream ID or index.

        Args:
            stream_id (str): The id of stream from the source file.

        Returns:
            StirlingStream: The stream encoded in the source.
        """

        this_stream = [
            stream for stream in self.streams if stream.stream_id == stream_id
        ]
        return this_stream[0] if len(this_stream) == 1 else None

    def get_streams(self, stream_type: str) -> List[StirlingStream]:
        """Returns a specific stream, specified by its stream ID or index.

        Args:
            stream_type (str): The type of stream to find the preferred stream for.

        Returns:
            List[StirlingStream]: The streams encoded in the source.
        """

        return [stream for stream in self.streams if stream.type == stream_type]

    def get_preferred_stream(
        self, stream_type: str
    ) -> Union[StirlingStream, StirlingStreamVideo, StirlingStreamAudio]:
        """Returns the preferred stream, specified by the type of stream.

        Args:
            stream_type (str): The type of stream to find the preferred stream for.

        Returns:
            int: The index of the preferred stream for the stream type.
        """

        this_stream = [
            stream
            for stream in self.streams
            if stream.stream_id == self.preferred[stream_type]
        ]

        return this_stream[0] if len(this_stream) == 1 else None


@dataclass
class StirlingMediaInfoCodecLibrary(StirlingClass):
    """StirlingMediaInfoCodecLibrary is a class representing the
    individual libraries used by encoders and decoders of the
    media framework.

    Attributes:
        name (str): The name of the library.
        encode (bool): Whether the library can encode.
        decode (bool): Whether the library can decode.
        experimental (bool): Whether the codec is marked as experimental.
    """

    name: str
    encode: bool = False
    decode: bool = False
    experimental: bool = False


@dataclass
class StirlingMediaInfoCodec(StirlingClass):
    """StirlingMediaInfoCodec is a class representing the
    individual encoders and decoders available to the media framework.

    Attributes:
        name (str): The short name of the codec.
        description (str, optional): A description of the codec.
        stream_type (str): The type of stream the codec can handle. Examples
            include "audio", "video", "subtitle", etc.
        lossless (bool): Whether the codec is capable of lossless encoding.
            This does not mean that the codec is lossless by default, but
            only that it can be used to encode lossless streams.
    """

    name: str
    description: str | None = None
    libraries: List[StirlingMediaInfoCodecLibrary] = field(default_factory=list)
    stream_type: str = "unknown"
    lossless: bool = False


@dataclass(kw_only=True)
class StirlingMediaInfoContainer(StirlingClass):
    """StirlingMediaInfoContainer is a class representing the
    individual output formats available from the media framework.

    Attributes:
        description (str): A description of the codec.
        file_extensions (List[str]): A list of file extensions that can be used with the container.
        encode (bool): Whether the container can be used in encoding operations.
        decode (bool): Whether the container can be used in decoding operations.
    """

    description: str
    file_extensions: List[str] = field(default_factory=list)
    file_mime_types: List[str] = field(default_factory=list)
    encode: bool = False
    decode: bool = False


@dataclass(kw_only=True)
class StirlingMediaFrameworkCapabilities(StirlingClass):
    """The capabilities of the framework."""

    codecs: List[StirlingMediaInfoCodec] = None
    containers: List[StirlingMediaInfoContainer] = None

    def get_codec_by_name(self, codec_name: str):
        for codec in self.codecs:
            if codec_name == codec.name:
                return codec
        return

    def get_container_by_extension(self, file_extension: str):
        for container in self.containers:
            for ext in container.file_extensions:
                if file_extension in self.file_extensions:
                    return ext


@dataclass
class StirlingMediaFrameworkOptions(StirlingClass):
    """Specify which version os the Media Framework to support.

    Version should be true semantic version or version match string.
    """

    version: str


@dataclass
class StirlingMediaFramework(StirlingClass, ABC):
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

    @abstractmethod
    def probe(self, source: str | Path) -> StirlingMediaInfo:
        """Probe the source file and return a StirlingMediaInfo object."""
        ...

    @abstractmethod
    def codec_container_supported(self, codec: str, container: str) -> bool:
        """Check if the codec and container are supported."""
        ...

    @abstractmethod
    def get_dependency(self) -> Path:
        """Get the path to the binary dependency."""
        return self.dependencies.get(self.name)
