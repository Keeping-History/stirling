import itertools
import re
from typing import List, Tuple

from pydantic.dataclasses import dataclass

from stirling.core import StirlingClass
from stirling.dependencies import StirlingDependency
from stirling.frameworks.ffmpeg.command import (
    StirlingMediaFrameworkFFMpegCommand,
)
from stirling.frameworks.media_info import (
    StirlingMediaInfoCodec,
    StirlingMediaInfoCodecLibrary,
)


@dataclass
class StirlingMediaInfoCodecParser(StirlingClass):
    def __init__(self, binary_transcoder: StirlingDependency):
        self._binary_transcoder = binary_transcoder

    @staticmethod
    def _get_codec_type(row: str) -> str:
        row = row.strip()
        if "V" in row[:3]:
            return "video"
        if "A" in row[:3]:
            return "audio"
        if "S" in row[:3]:
            return "subtitle"
        return "data" if "D" in row[:3] else "unknown"

    @staticmethod
    def _get_codec_name(row: str) -> str:
        return row[8:].split(" ", 1)[0]

    @staticmethod
    def _get_codec_features(row: str) -> Tuple[bool, bool]:
        """Determine the framework specific features of each codec.
        This can be expanded to include more features in the future."""

        interframe = row[4] == "I"
        lossless = row[6] == "S"
        return interframe, lossless

    @staticmethod
    def _get_codec_actions(row: str) -> Tuple[bool, bool]:
        """Determine whether a codec can be used to encode or decode."""

        encode = "E" in row[:3]
        decode = "D" in row[:2]
        return encode, decode

    @staticmethod
    def _get_codec_description(row: str) -> str:
        full_description = row[8:].split(" ", 1)[1].strip()

        start = full_description.find("coders: ")
        end = start - 4
        if start > 0:
            full_description = full_description[:end]
        return full_description

    @staticmethod
    def _get_codec_libraries_filtered(
        libraries: List,
    ) -> List[StirlingMediaInfoCodecLibrary]:
        """Filters out duplicate libraries."""
        for i, lib in enumerate(libraries):
            for origin_lib in libraries:
                if origin_lib[0] == lib[0] and (
                    origin_lib[1] != lib[1] or origin_lib[2] != lib[2]
                ):
                    libraries[i][1] = True
                    libraries[i][2] = True

        libraries.sort()
        libraries = [libraries for libraries, _ in itertools.groupby(libraries)]
        return [
            StirlingMediaInfoCodecLibrary(
                name=lib[0],
                encode=lib[1],
                decode=lib[2],
                experimental=False,
            )
            for lib in libraries
        ]

    def _get_codec_libraries(
        self, row: str
    ) -> List[StirlingMediaInfoCodecLibrary]:
        """Get the particular codec libraries, and their encode/decode status,
        for a given codec."""

        libraries = []

        codec_actions = [
            ("encoders: ", True, False),
            ("decoders: ", False, True),
        ]
        for codec_action in codec_actions:
            codec_search = re.search(r"\(" + codec_action[0] + "(.*?) \)", row)
            if codec_search is None:
                codec_mode = self._get_codec_actions(row)
                libraries.append(
                    [self._get_codec_name(row), codec_mode[0], codec_mode[1]]
                )

            else:
                available_libraries = codec_search[1].strip().split(" ")
                libraries.extend(
                    [library, codec_action[1], codec_action[2]]
                    for library in available_libraries
                )
        return self._get_codec_libraries_filtered(libraries)

    def get(self) -> List[StirlingMediaInfoCodec]:
        """A static method that queries FFMpeg and returns a list of available
        codecs.

        Returns:
            List[StirlingMediaInfoCodec]
        """

        all_codecs = []

        options = {
            "hide_banner": True,
        }
        cmd_output = StirlingMediaFrameworkFFMpegCommand(
            binary_dependency=self._binary_transcoder,
            options=options,
            keyword_arguments={
                "codecs": True,
            },
        ).run()

        if cmd_output == "":
            raise ValueError("Unable to get supported codecs from FFMpeg.")

        lines = list(
            filter(
                None, cmd_output[cmd_output.find("------\n") + 7 :].split("\n")
            )
        )
        for row in lines:
            name, libraries, description = (
                self._get_codec_name(row),
                self._get_codec_libraries(row),
                self._get_codec_description(row),
            )
            this_codec = StirlingMediaInfoCodec(
                name=name,
                description=description,
                libraries=libraries,
                stream_type=self._get_codec_type(row),
                lossless=self._get_codec_features(row)[1],
            )

            all_codecs.append(this_codec)

        return all_codecs
