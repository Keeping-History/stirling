import json
import subprocess
from dataclasses import dataclass, field
from typing import List

import argunparse
import simpleeval

from core import core


@dataclass
class StirlingMediaFramework(core.StirlingClass):
    """StirlingMediaFramework is a class for handling the underlying system
    media framework used to interact with media files.


    Attributes:
        name (str): The encoder framework to use. For example, `ffmpeg` is a
            media framework that can be used to interact with video and audio
            files; `Mencoder` and `MLT` are other examples of media frameworks.

        version (str): The version of the encoder framework to use. Helpful
            when multiple versions of the same framework are needed to support
            a specific Video Compression Format (VCS).
    """

    name: str
    version: str
    encoders: List[str] = field(default_factory=list)
    formats: List[str] = field(default_factory=list)


@dataclass(kw_only=True)
class StirlingMediaFrameworkFFmpeg(StirlingMediaFramework):
    """StirlingMediaFrameworkFFmpeg is a class for using the `ffmpeg` Media
    Framework to interact with media files and their metadata.

    Note that `ffmpeg` will require additional arguments to be passed at build
    time to enable support for specific Video Compression Formats (VCFs).
    For MacOS, the preferred `ffmpeg` distribution, installable using Homebrew,
    is available at https://github.com/skyzyx/homebrew-ffmpeg.
    """

    name: str = "FFmpeg"
    binary_transcoder: str = "ffmpeg"
    binary_probe: str = "ffprobe"
    version: str = "5.1.2"
    default_options: dict = field(default_factory=dict)

    def __post_init__(self):
        self.default_options = {
            "hide_banner": True,
            "y": True,
            "loglevel": "warning",
        }

    def cmd(self):
        return (
            self.binary_transcoder,
            self.unparser.unparse(**self.default_options),
        )

    def resize(self, width: float, height: float, relative: bool = False) -> tuple:
        if relative:
            return {"-vf": f"scale=iw*{width}:ih*{height}"}
        return {"-vf": f"scale={width}:{height}"}

    def unparser(self):
        return argunparse.ArgumentUnparser(
            long_opt="-", opt_value=" ", begin_delim="", end_delim=""
        )


@dataclass
class StirlingMediaInfoFFmpeg(core.StirlingMediaInfo):
    def __post_init__(self):

        # Check to make sure the appropriate binary files we need are installed.
        assert core.check_dependencies_binaries(
            [self.binary_transcoder, self.binary_probe]
        ), AssertionError("Missing required binaries.")

        options = {
            "loglevel": "quiet",
            "hide_banner": True,
            "show_error": False,
            "show_format": True,
            "show_streams": True,
            "show_private_data": True,
            "print_format": "json",
        }

        cmd = "ffprobe " + core.ffmpeg_unparser.unparse(str(self.source), **options)

        # Check if we can probe the input file.
        cmd_output = subprocess.getstatusoutput(cmd)

        # If we don't get any output from above, then we can't probe the file.
        # Return an empty StirlingMediaInfo() object.
        if cmd_output[0] != 0 or cmd_output[1] == "":
            return

        streams = json.loads(cmd_output[1])["streams"]

        for stream in streams:
            match stream["codec_type"]:
                case "video":
                    self.__create_video_stream(stream)
                case "audio":
                    self.__create_audio_stream(stream)
                case "subtitle":
                    self.__create_text_stream(stream)

        # If a specific audio or video stream are not passed in as arguments,
        # attempt to get the preferred video and audio streams based on their
        # quality, bitrate, etc.
        self.preferred["video"] = self.__auto_set_preferred("video")
        self.preferred["audio"] = self.__auto_set_preferred("audio")

    def get_stream(self, type: str, id: int):
        match type:
            case "video":
                return self.__get_video_stream(id)
            case "audio":
                return self.__get_audio_stream(id)
            case "text":
                return self.__get_text_stream(id)
            case _:
                raise ValueError("Invalid stream type.")

    def get_preferred_stream(self, stream_type: str):
        match stream_type:
            case "video":
                return self.__get_video_stream(self.preferred["video"])
            case "audio":
                return self.__get_audio_stream(self.preferred["audio"])
            case "text":
                return self.__get_text_stream(self.preferred["text"])
            case _:
                raise ValueError("Invalid stream type.")

    def __get_video_stream(self, stream_id: int):
        return next(
            (stream for stream in self.video_streams if stream.stream == stream_id)
        )

    def __get_audio_stream(self, stream_id: int):
        return next(
            (stream for stream in self.audio_streams if stream.stream == stream_id)
        )

    def __get_text_stream(self, stream_id: int):
        return next(
            (stream for stream in self.text_streams if stream.stream == stream_id)
        )

    def __auto_set_preferred(self, type: str):
        """Find the preferred stream based on it's metadata.

        When a stream is not specified specifically in the arguments, we need
        to determine the best stream to use on behalf of the user. This is done
        by some simple calculations based on the stream's metadata.

        Args:
            type (str): The type of stream to find the preferred stream for.

        Returns:
            int: The index of the preferred stream.
        """
        m = {}
        match type:
            case "video":
                for stream in self.video_streams:
                    m[stream.stream] = [stream.width * stream.height]
            case "audio":
                for stream in self.audio_streams:
                    m[stream.stream] = [stream.bitrate]
        return max(m, key=m.get, default=None)

    def __create_text_stream(self, stream: dict):
        dispositions = []
        if "dispositions" in stream:
            for k, v in stream["dispositions"]:
                if v == 1:
                    dispositions.append(k)

        self.text_streams.append(
            core.StreamText(
                stream=self.__set_default(stream, "index"),
                duration=float(self.__set_default(stream, "duration")),
                codec=self.__set_default(stream, "codec_name"),
                start_time=self.__set_default(stream, "start_time"),
                dispositions=dispositions,
                language=self.__set_default(stream["tags"], "language", "und"),
                channel_layout=self.__set_default(stream, "channel_layout"),
            )
        )

    def __create_audio_stream(self, stream: dict):
        self.audio_streams.append(
            core.StreamAudio(
                stream=self.__set_default(stream, "index"),
                duration=float(self.__set_default(stream, "duration")),
                codec=self.__set_default(stream, "codec_name"),
                profile=self.__set_default(stream, "profile"),
                bitrate=self.__set_default(stream, "bit_rate"),
                sample_rate=self.__set_default(stream, "sample_rate"),
                channels=self.__set_default(stream, "channels"),
                channel_layout=self.__set_default(stream, "channel_layout"),
            )
        )

    def __create_video_stream(self, stream: dict):
        self.video_streams.append(
            core.StreamVideo(
                stream=self.__set_default(stream, "index"),
                duration=float(self.__set_default(stream, "duration")),
                codec=self.__set_default(stream, "codec_name"),
                profile=self.__set_default(stream, "profile"),
                bitrate=self.__set_default(stream, "bit_rate"),
                width=self.__set_default(stream, "width"),
                height=self.__set_default(stream, "height"),
                frame_rate=float(
                    simpleeval.simple_eval(self.__set_default(stream, "avg_frame_rate"))
                ),
                aspect=self.__set_default(stream, "display_aspect_ratio", "0:0").split(
                    ":"
                ),
                scan_type=self.__set_default(stream, "field_order", "unknown"),
                color_bits=self.__set_default(stream, "bits_per_raw_sample", 8),
                color_model=self.__set_default(stream, "pix_fmt", "unknown"),
            )
        )

    def __set_default(self, obj: dict, key: str, default: bool = None):
        if key in obj:
            return obj[key]
        else:
            return default
