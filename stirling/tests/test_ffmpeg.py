import os
from pathlib import Path

import pytest

from stirling.dependencies import StirlingDependency
from stirling.frameworks.base import (
    StirlingMediaInfoCodec,
    StirlingMediaInfoCodecLibrary,
    StirlingMediaInfoContainer,
    StirlingStreamText,
)
from stirling.frameworks.ffmpeg.core import StirlingMediaFrameworkFFMpeg
from stirling.frameworks.ffmpeg.version import check_ffmpeg_version

test_video_file = Path(Path(os.getcwd()) / "examples/test_cspan.mp4")
test_audio_file = Path(Path(os.getcwd()) / "examples/test_cspan.mp3")
binary_transcoder = "ffmpeg"
version = ">=6.0.0"


def _get_framework():
    return StirlingMediaFrameworkFFMpeg()


ffmpeg_probe_dependency: StirlingDependency = _get_framework().dependencies.get(
    "ffprobe"
)
ffmpeg_transcoder_dependency: StirlingDependency = _get_framework().dependencies.get(
    "ffmpeg"
)

video_file_media_info = _get_framework().probe(source=test_video_file)
audio_file_media_info = _get_framework().probe(source=test_audio_file)

video_file_video_stream = video_file_media_info.get_streams("video")[0]
video_file_audio_stream = video_file_media_info.get_streams("audio")[0]
audio_file_audio_stream = audio_file_media_info.get_streams("audio")[0]

text_stream = StirlingStreamText(
    stream_id=2,
    duration=10,
    start_time=0,
    language="eng",
    dispositions=[{"default": True}],
)


def test_ffmpeg_version():
    assert check_ffmpeg_version(ffmpeg_transcoder_dependency, version) is None


@pytest.mark.parametrize(
    "data,expected",
    [
        (
            [0, 0, 0, 0, video_file_video_stream],
            {"-vf": "crop=0:0:0:0"},
        ),  # Crop by width, height, x, y coordinates
        (
            [(6, 9), video_file_video_stream],
            {"-vf": "crop=ih/54:ih"},
        ),  # Crop by aspect ratio
        (
            [(6, 9), (0, 0), video_file_video_stream],
            {"-vf": "crop=ih/54:ih:0:0"},
        ),  # Crop by aspect ratio and x, y coordinates
        (
            [test_video_file, video_file_video_stream],
            {"-vf": "crop=1024:576:0:0"},
        ),  # Crop by aspect ratio and x, y coordinates
    ],
    ids=[
        "test_crop_video_w_h_x_y",
        "test_crop_video_aspect_ratio",
        "test_crop_video_aspect_ratio_x_y",
        "test_crop_video_autodetect",
    ],
)
def test_crop_video(data: dict, expected: dict):
    assert _get_framework().crop(*data) == expected


@pytest.mark.parametrize(
    "data,expected",
    [
        ([640, 480, video_file_video_stream], {"-vf": "scale=640:480"}),
        ([(6, 9), video_file_video_stream], {"-vf": "scale=iw*6:ih*9"}),
    ],
    ids=["test_resize_video_w_h", "test_resize_video_aspect_ratio"],
)
def test_resize_video(data, expected):
    assert _get_framework().resize(*data) == expected


@pytest.mark.parametrize(
    "data,expected",
    [
        (
            ["0", "10", video_file_video_stream],
            {"-ss": "0", "-to": "10", "-accurate_seek": True},
        ),
        (
            ["0", "10", video_file_video_stream],
            {"-ss": "0", "-to": "10", "-accurate_seek": True},
        ),
        # ([0, 10, text_stream], pytest.raises(NotImplementedError)), # TODO: WHY DOES THIS NOT WORK?
    ],
    ids=["test_trim_video_start_end", "test_trim_audio_start_end"],
)
def test_trim_video(data, expected):
    assert _get_framework().trim(*data) == expected


@pytest.mark.parametrize(
    "data,expected",
    [
        (
            ["10", "30.2", audio_file_audio_stream],
            {"-ss": "10", "-to": "30.2", "-accurate_seek": True},
        ),
    ],
    ids=["test_trim_audio_start_end"],
)
def test_trim_audio(data, expected):
    assert _get_framework().trim(*data) == expected


@pytest.mark.parametrize(
    "data,expected",
    [
        (
            "h264",
            StirlingMediaInfoCodec(
                name="h264",
                description="H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10",
                libraries=[
                    StirlingMediaInfoCodecLibrary(
                        name="h264",
                        encode=False,
                        decode=True,
                        experimental=False,
                    ),
                    StirlingMediaInfoCodecLibrary(
                        name="h264_cuvid",
                        encode=False,
                        decode=True,
                        experimental=False,
                    ),
                    StirlingMediaInfoCodecLibrary(
                        name="h264_nvenc",
                        encode=True,
                        decode=False,
                        experimental=False,
                    ),
                    StirlingMediaInfoCodecLibrary(
                        name="h264_omx",
                        encode=True,
                        decode=False,
                        experimental=False,
                    ),
                    StirlingMediaInfoCodecLibrary(
                        name="h264_v4l2m2m",
                        encode=True,
                        decode=True,
                        experimental=False,
                    ),
                    StirlingMediaInfoCodecLibrary(
                        name="h264_vaapi",
                        encode=True,
                        decode=False,
                        experimental=False,
                    ),
                    StirlingMediaInfoCodecLibrary(
                        name="libx264",
                        encode=True,
                        decode=False,
                        experimental=False,
                    ),
                    StirlingMediaInfoCodecLibrary(
                        name="libx264rgb",
                        encode=True,
                        decode=False,
                        experimental=False,
                    ),
                    StirlingMediaInfoCodecLibrary(
                        name="nvenc",
                        encode=True,
                        decode=False,
                        experimental=False,
                    ),
                    StirlingMediaInfoCodecLibrary(
                        name="nvenc_h264",
                        encode=True,
                        decode=False,
                        experimental=False,
                    ),
                ],
                stream_type="video",
                lossless=True,
            ),
        ),
        (
            "av1",
            StirlingMediaInfoCodec(
                name="av1",
                description="Alliance for Open Media AV1",
                libraries=[
                    StirlingMediaInfoCodecLibrary(
                        name="libaom-av1",
                        encode=True,
                        decode=True,
                        experimental=False,
                    )
                ],
                stream_type="video",
                lossless=False,
            ),
        ),
        (
            "tak",
            StirlingMediaInfoCodec(
                name="tak",
                description="TAK (Tom's lossless Audio Kompressor)",
                libraries=[
                    StirlingMediaInfoCodecLibrary(
                        name="tak",
                        encode=False,
                        decode=True,
                        experimental=False,
                    ),
                ],
                stream_type="audio",
                lossless=True,
            ),
        ),
    ],
)
def test_supported_codecs(data, expected):
    for a in _get_framework().capabilities.codecs:
        if a.name == data:
            assert a == expected


@pytest.mark.parametrize(
    "data,expected",
    [
        (
            "3DO STR",
            StirlingMediaInfoContainer(
                description="3DO STR",
                file_extensions=["3dostr"],
                encode=False,
                decode=True,
            ),
        ),
        (
            "3GP2 (3GPP2 file format)",
            StirlingMediaInfoContainer(
                description="3GP2 (3GPP2 file format)",
                file_extensions=["3g2"],
                encode=True,
                decode=False,
            ),
        ),
        (
            "CRI ADX",
            StirlingMediaInfoContainer(
                description="CRI ADX",
                file_extensions=["adx"],
                encode=True,
                decode=True,
            ),
        ),
    ],
)
def test_supported_containers(data, expected):
    for a in _get_framework().capabilities.containers:
        if a.description == data:
            assert a == expected


from stirling.frameworks.ffmpeg.constants import FFMpegCommandValueDimensions


def test_ffmpeg_command_value_dimensions_get():
    dims = FFMpegCommandValueDimensions(1, 2, 3, 4)
    assert dims.get() == "1:2:3:4"
    dims = FFMpegCommandValueDimensions(1, 2)
    assert dims.get() == "1:2"


if __name__ == "__main__":
    test_ffmpeg_command_value_dimensions_get()
