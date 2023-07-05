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


# -ar[:stream_specifier] freq (input/output,per-stream)
# Set the audio sampling frequency. For output streams it is set by default to the frequency of the corresponding input stream. For input streams this option only makes sense for audio grabbing devices and raw demuxers and is mapped to the corresponding demuxer options.
#
# -aq q (output)
# Set the audio quality (codec-specific, VBR). This is an alias for -q:a.
#
# -ac[:stream_specifier] channels (input/output,per-stream)
# Set the number of audio channels. For output streams it is set by default to the number of input audio channels. For input streams this option only makes sense for audio grabbing devices and raw demuxers and is mapped to the corresponding demuxer options.
#
# -acodec codec (input/output)
# Set the audio codec. This is an alias for -codec:a.
#
# -sample_fmt[:stream_specifier] sample_fmt (output,per-stream)
# Set the audio sample format. Use -sample_fmts to get a list of supported sample formats.
# https://usage.toolstud.io/docs/ffmpeg/usage/sample_fmts/

# raw PCM A-law	X	X
# raw PCM mu-law	X	X
# raw PCM Archimedes VIDC	X	X
# raw PCM signed 8 bit	X	X
# raw PCM signed 16 bit big-endian	X	X
# raw PCM signed 16 bit little-endian	X	X
# raw PCM signed 24 bit big-endian	X	X
# raw PCM signed 24 bit little-endian	X	X
# raw PCM signed 32 bit big-endian	X	X
# raw PCM signed 32 bit little-endian	X	X
# raw PCM signed 64 bit big-endian	X	X
# raw PCM signed 64 bit little-endian	X	X
# raw PCM unsigned 8 bit	X	X
# raw PCM unsigned 16 bit big-endian	X	X
# raw PCM unsigned 16 bit little-endian	X	X
# raw PCM unsigned 24 bit big-endian	X	X
# raw PCM unsigned 24 bit little-endian	X	X
# raw PCM unsigned 32 bit big-endian	X	X
# raw PCM unsigned 32 bit little-endian	X	X
# raw PCM 16.8 floating point little-endian		X
# raw PCM 24.0 floating point little-endian		X
# raw PCM floating-point 32 bit big-endian	X	X
# raw PCM floating-point 32 bit little-endian	X	X
# raw PCM floating-point 64 bit big-endian	X	X
# raw PCM floating-point 64 bit little-endian	X	X
