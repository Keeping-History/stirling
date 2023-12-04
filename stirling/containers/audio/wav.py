from pydantic.dataclasses import dataclass

from stirling.containers.base import StirlingMediaContainer


@dataclass
class StirlingMediaContainerAudioWAV(StirlingMediaContainer):
    name: str = "wav"
    description: str = "Waveform Audio File Format"
    file_extension: str = "wav"
    file_mime_type: str = "audio/wav"

    def __post_init__(self):
        self.supported_codecs = []
