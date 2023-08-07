import json
from collections import Counter
from dataclasses import field
from pathlib import Path
from typing import List

import simpleeval
from langcodes import Language, standardize_tag
from pydantic.dataclasses import dataclass

from stirling.core import StirlingClass
from stirling.dependencies import StirlingDependency
from stirling.frameworks.base import StirlingMediaInfo
from stirling.frameworks.base import (
    StirlingStreamAudio,
    StirlingStreamText,
    StirlingStreamVideo,
)
from stirling.frameworks.ffmpeg.command import (
    StirlingMediaFrameworkFFMpegCommand,
)


@dataclass
class StirlingMediaFrameworkFFMpegProbe(StirlingClass):
    """StirlingMediaFrameworkFFMpegProbe is a class that is used to probe media files using FFMpeg."""

    source: Path
    transcoder_binary_dependency: StirlingDependency
    probe_binary_dependency: StirlingDependency
    default_cmd_options: dict | None = field(default_factory=dict)

    @staticmethod
    def create_text_stream(raw_stream: dict):
        dispositions = []
        if "dispositions" in raw_stream:
            dispositions.extend(
                k for k, v in raw_stream["dispositions"] if v == 1
            )
        return StirlingStreamText(
            stream_id=raw_stream.get("index"),
            duration=float(raw_stream.get("duration")),
            start_time=raw_stream.get("start_time"),
            dispositions=dispositions,
            language=Language.get(
                standardize_tag(raw_stream.get("tags")), normalize=False
            ).language,
        )

    @staticmethod
    def create_audio_stream(raw_stream: dict) -> StirlingStreamAudio:
        return StirlingStreamAudio(
            stream_id=raw_stream.get("index"),
            duration=float(raw_stream.get("duration")),
            codec=raw_stream.get("codec_name"),
            channels=raw_stream.get("channels"),
            bit_rate=raw_stream.get("bit_rate"),
            sample_rate=raw_stream.get("sample_rate"),
            channel_layout=raw_stream.get("channel_layout"),
            profile=raw_stream.get("profile"),
        )

    @staticmethod
    def create_video_stream(raw_stream: dict) -> StirlingStreamVideo:
        if (
            "duration" not in raw_stream
            and "tags" in raw_stream
            and "DURATION" in raw_stream.get("tags")
        ):
            raw_stream["duration"] = raw_stream.get("tags").get("DURATION")

        if not raw_stream["duration"]:
            raise ValueError("Duration is required.")

        return StirlingStreamVideo(
            stream_id=raw_stream.get("index"),
            duration=raw_stream.get("duration"),
            width=raw_stream.get("width"),
            height=raw_stream.get("height"),
            codec=raw_stream.get("codec_name"),
            profile=raw_stream.get("profile"),
            bit_rate=raw_stream.get("bit_rate"),
            frame_rate=float(
                simpleeval.simple_eval(raw_stream.get("avg_frame_rate"))
            ),
            aspect=raw_stream.get("display_aspect_ratio").split(":"),
            scan_type=raw_stream.get("field_order"),
            color_model=raw_stream.get("pix_fmt"),
        )

    @staticmethod
    def auto_set_preferred(stream_type: str, streams: List):
        """Find the preferred stream based on its metadata.

        When a stream is not specified specifically in the arguments, we need
        to determine the best stream to use on behalf of the user. This is done
        by some simple calculations based on the stream's metadata.

        Args:
            stream_type (str): The type of stream to find the preferred stream for.
            streams (List): A list of streams to search through.

        Returns:
            int: The index of the automatically-set preferred stream.
        """

        m = {}
        match stream_type:
            case "video":
                for stream in [x for x in streams if x.type == "video"]:
                    m[stream.stream_id] = [stream.width * stream.height]
            case "audio":
                for stream in [x for x in streams if x.type == "audio"]:
                    m[stream.stream_id] = [stream.bit_rate]
        return max(m, key=m.get, default=None)

    def probe(self) -> StirlingMediaInfo:
        output_streams = []
        options = {
            "i": self.source,
            "loglevel": "quiet",
            "hide_banner": True,
            "show_error": False,
            "show_format": True,
            "show_streams": True,
            "show_private_data": True,
            "print_format": "json",
        }

        cmd_output = StirlingMediaFrameworkFFMpegCommand(
            dependency=self.probe_binary_dependency,
            options=options,
        ).run()

        if cmd_output == "":
            raise ValueError("Unable to get supported codecs from FFMpeg.")

        streams = json.loads(cmd_output)["streams"]

        for stream in streams:
            match stream["codec_type"]:
                case "video":
                    output_streams.append(
                        StirlingMediaFrameworkFFMpegProbe.create_video_stream(
                            stream
                        )
                    )
                case "audio":
                    output_streams.append(
                        StirlingMediaFrameworkFFMpegProbe.create_audio_stream(
                            stream
                        )
                    )
                case "subtitle":
                    output_streams.append(
                        StirlingMediaFrameworkFFMpegProbe.create_text_stream(
                            stream
                        )
                    )

        preferred = {
            "video": StirlingMediaFrameworkFFMpegProbe.auto_set_preferred(
                "video", output_streams
            ),
            "audio": StirlingMediaFrameworkFFMpegProbe.auto_set_preferred(
                "audio", output_streams
            ),
        }

        return StirlingMediaInfo(
            streams=output_streams,
            preferred=preferred,
            source=str(self.source),
        )

    def letterbox_detect(self, stream_id: int):
        found_crop_positions = []

        options = {
            "i": str(self.source),
            "map": f"{stream_id}",
            "hide_banner": True,
            "frames:v": 100,
            "vf": "cropdetect",
            "y": True,
            "f": "mp4",
        }

        # We still need an output file, even if we are not using it.
        arguments = ["/dev/null"]

        cmd_output = StirlingMediaFrameworkFFMpegCommand(
            arguments=arguments,
            binary_dependency=self.transcoder_binary_dependency,
            options=options,
        ).run()

        for crop in cmd_output.splitlines():
            if crop.find("crop=") > 0:
                width, height, x, y = crop[crop.find("crop=") + 5 :].split(":")
                found_crop_positions.append(
                    [int(width), int(height), int(x), int(y)]
                )
        result_counter = Counter(tuple(item) for item in found_crop_positions)

        return list(max(result_counter))
