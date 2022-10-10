from array import array
from dataclasses import dataclass
from datetime import datetime
import json
import subprocess
import sys

from core import helpers as helpers

required_binaries = ["ffprobe"]

@dataclass
class SourceInfo:
    streams_count: int
    size: int # bits
    container_format: str #  tags: major_brand
    created: datetime
    bitrate: float # in bits per second


@dataclass
class Stream:
    codec: str
    duration: float # in seconds
    content_type: str # audio or video
    streams_count: int
    codec: str
    profile: str

@dataclass
class StreamVideo(Stream):
    width: int
    height: int
    frame_rate: float # avg_frame_rate
    scan_type: str # progressive or one of the interlace formats (tt, tb, bt, bb)
    color_space: str
    color_bits: int # bits_per_raw_sample
    color_model: str # pix_fmt

    content_type: str = "video"
    aspect: array = array[1, 1] # display_aspect_ratio

@dataclass
class StreamAudio(Stream):
    sample_rate: int
    channels: int
    channel_layout: str

    language: str = "eng"
    content_type: str = "audio"

def probe_media_file(input):

    ffprobe_options = "-hide_banner -loglevel quiet -show_error -show_format -show_streams -show_programs -show_chapters -show_private_data -print_format json"
    # Check if we can probe the input file.
    ffmpeg_proc = subprocess.getstatusoutput(
        ["ffprobe {} '{}'".format(ffprobe_options, input)]
    )

    if ffmpeg_proc[0] != 0:
        return None

    return json.loads(ffmpeg_proc[1])


def get_input_streams(job):

    streams, video_stream, audio_stream, hls_disable = (
        job["source"]["info"]["streams"],
        job["arguments"]["input_video_stream"],
        job["arguments"]["input_audio_stream"],
        job["arguments"]["hls_disable"],
    )

    if hls_disable:
        if audio_stream == -1:
            audio_stream = get_best_audio(
                get_input_streams_from_probe(streams, "audio")
            )
    else:
        if video_stream == -1:
            video_stream = get_best_video(
                get_input_streams_from_probe(streams, "video")
            )
            if audio_stream == -1:
                audio_stream = get_best_audio(
                    get_input_streams_from_probe(streams, "audio")
                )
        else:
            audio_stream = audio_stream

    (
        job["source"]["input"]["video_stream"],
        job["source"]["input"]["audio_stream"],
    ) = (video_stream, audio_stream)
    helpers.log(
        job,
        "Using video input stream {} ".format(job["source"]["input"]["video_stream"]),
    )
    helpers.log(
        job,
        "Using audio input stream {} ".format(job["source"]["input"]["audio_stream"]),
    )

    return job


def get_input_streams_from_probe(probe_streams, stream_type):
    # Get the input streams based on the codec type.
    holder = []
    for i in range(len(probe_streams)):
        if probe_streams[i].get("codec_type") == stream_type:
            holder.append((i, probe_streams[i]))
    return holder


def get_best_video(probe_streams):
    if len(probe_streams) > 0:
        v = {}
        for stream in probe_streams:
            v[stream[0]] = [stream[1].get("width") * stream[1].get("height")]

    return max(v, key=v.get)


def get_best_audio(probe_streams):
    if len(probe_streams) > 0:
        a = {}
        for stream in probe_streams:
            a[stream[0]] = [stream[1].get("bit_rate")]

    return max(a, key=a.get)


def probe(job):
    # Check to make sure the appropriate binary files we need are installed.
    assert helpers.check_dependencies_binaries(required_binaries), helpers.log(
        helpers.check_dependencies_binaries(required_binaries)
    )

    # Check if we can probe the input file.
    job["source"]["info"] = probe_media_file(job["source"]["input"]["filename"])
    if job["source"]["info"] is None:
        helpers.log(
            "Could not probe the input file {}.".format(
                job["source"]["input"]["filename"]
            )
        )
        sys.exit(1)

    helpers.log(
        job, "Probed media file: " + json.dumps(job["source"]["info"], indent=4)
    )

    # Get the input streams.
    job = get_input_streams(job)

    #  The video must be longer than zero (0) seconds.
    stream_duration = float(
        job["source"]["info"]["streams"][(job["source"]["input"]["video_stream"])][
            "duration"
        ]
    )
    assert stream_duration > 0, "couldn't get duration of input file {}".format(
        job["source"]["input"]["filename"]
    )

    # The video must be shorter than 24 hours (86400 seconds)
    assert stream_duration <= 86400, "stream is over 24 hours, not supported {}".format(
        job["source"]["input"]["filename"]
    )

    # The video and audio must have the input streams we've either specified
    # automatically or either manually through the --input-audio-stream and
    # --input-video-stream argument.
    assert (
        job["source"]["input"]["video_stream"] >= 0
    ), "couldn't get video stream for file {}".format(
        str(job["source"]["input"]["filename"])
    )

    assert (
        job["source"]["input"]["audio_stream"] >= 0
    ), "couldn't get audio stream for file  {}".format(
        str(job["source"]["input"]["filename"])
    )
    return job
