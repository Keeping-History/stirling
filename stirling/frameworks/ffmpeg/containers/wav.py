from dataclasses import field

from pydantic.dataclasses import dataclass

from stirling.containers.base import StirlingMediaContainer
from stirling.frameworks.ffmpeg.codecs.pcm import StirlingCodecAudioPCM


@dataclass
class StirlingMediaContainerWav(StirlingMediaContainer):
    name: str = "Waveform Audio File"
    file_extension: str = "wav"
    file_mime_type: str = "audio/wav"
    supported_codecs: list = field(
        default_factory=lambda: [StirlingCodecAudioPCM]
    )
