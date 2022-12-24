from dataclasses import dataclass, field
from typing import List

from stirling import core, framework, encoders

@dataclass
class StirlingMediaContainer(core.StirlingClass):

    name: str
    file_extension: str
    file_mime_type: str
    def __post_init__(self):
        return super().__post_init__()
