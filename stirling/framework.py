from dataclasses import dataclass, field
from typing import List, Type

from stirling import core, container, encoders


@dataclass
class StirlingMediaFramework(core.StirlingClass):
    """StirlingMediaFramework is a class for handling the underlying system
    media framework used to interact with media files.


    Attributes:
        name (str): The encoder framework to use. For example, `FFMpeg` is a
            media framework that can be used to interact with video and audio
            files; `Mencoder` and `MLT` are other examples of media frameworks.

        version (str): The version of the encoder framework to use. Helpful
            when multiple versions of the same framework are needed to support
            a specific Video Compression Format (VCS).
    """

    name: str
    version: str
    encoders: List[Type[encoders.StirlingEncoder]] = field(default_factory=list)
    formats: List[Type[container.StirlingMediaContainer]] = field(default_factory=list)
