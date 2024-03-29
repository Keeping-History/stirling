import json
import subprocess
from dataclasses import dataclass, field
from typing import List

import simpleeval

from core import args, definitions, helpers

required_binaries = ["ffprobe"]


@dataclass
class StirlingMediaInfo(definitions.StirlingClass):
    source: str = field(default=None)
    video_streams: List[definitions.StreamVideo] = field(default_factory=list)
    audio_streams: List[definitions.StreamAudio] = field(default_factory=list)
    text_streams: List[definitions.StreamText] = field(default_factory=list)
    preferred: dict = field(default_factory=dict)

    def __post_init__(self):

        # Check to make sure the appropriate binary files we need are installed.
        assert helpers.check_dependencies_binaries(required_binaries), AssertionError(
            "Missing required binaries."
        )

        options = {
            "loglevel": "quiet",
            "hide_banner": True,
            "show_error": False,
            "show_format": True,
            "show_streams": True,
            "show_private_data": True,
            "print_format": "json",
        }

        cmd = "ffprobe " + args.ffmpeg_unparser.unparse(str(self.source), **options)

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
            definitions.StreamText(
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
            definitions.StreamAudio(
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
            definitions.StreamVideo(
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
