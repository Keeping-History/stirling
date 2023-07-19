from pydantic.dataclasses import dataclass

from stirling.containers.base import StirlingMediaContainer


@dataclass
class StirlingMediaContainerAudioMP3(StirlingMediaContainer):
    name: str = "mp3"
    description: str = "MP3 (MPEG audio layer 3) Format"
    file_extension: str = "mp3"
    file_mime_type: str = "audio/mpeg"

    def __post_init__(self):
        self.supported_codecs = []
