from pydantic.dataclasses import dataclass

from stirling.codecs.base import StirlingMediaCodec
from stirling.core import StirlingClass


@dataclass
class StirlingMediaContainer(StirlingClass):
    """The base class for a container object. Containers are file formats
    that can be used to either read or write
    streams from various codecs to.

    Attributes:
        name (str): The name, or description, of the container.
        file_extension (str): The file extension of the container.
        file_mime_type (str): The MIME type of the container.
        supported_codecs (list[[StirlingMediaCodec] | None): A list of
            codecs that are supported by the container.
    """

    name: str
    file_extension: str
    file_mime_type: str
    supported_codecs: list[StirlingMediaCodec] | None = None
