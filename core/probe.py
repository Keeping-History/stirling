from dataclasses import dataclass, field
import json
import subprocess
import argunparse
from typing import List
import simpleeval

from pathlib import Path
from core import helpers, jobs, definitions, args

required_binaries = ["ffprobe"]


@dataclass
class StreamVideo():
    stream: int

    duration: float
    codec: str
    profile: str
    bitrate: int

    width: int
    height: int
    frame_rate: float # avg_frame_rate
    color_model: str
    aspect: List

    color_bits: int = 8

    scan_type: str = "unknown"
    content_type: str = "video"

@dataclass
class StreamAudio():
    stream: int

    duration: float
    codec: str
    profile: str
    bitrate: int

    sample_rate: int
    channels: int
    channel_layout: str

    content_type: str = "audio"

@dataclass
class StreamText():
    stream: int

    duration: float
    codec: str
    start_time: float

    dispositions: list
    language: str = "und" # undetermined

    content_type: str = "subtitle"

@dataclass
class MediaInfo(definitions.StirlingClass):
    video_streams: List[StreamVideo] = None
    audio_streams: List[StreamAudio] = None
    text_streams: List[StreamText] = None

def probe_media_file(input: Path):
    options = {
        'hide_banner': True,
        'loglevel': "quiet",
        'show_error': False,
        'show_format': True,
        'show_streams': True,
        'show_programs': True,
        'show_chapters': True,
        'show_private_data': True,
        'print_format': "json",
    }

    source = { str(input) }
    cmd = "ffprobe " + args.default_unparser.unparse(*source, **options)

    # Check if we can probe the input file.
    ffmpeg_proc = subprocess.getstatusoutput(cmd)

    print(ffmpeg_proc)
    if ffmpeg_proc[0] != 0:
        return MediaInfo()

    streams = json.loads(ffmpeg_proc[1])["streams"]

    probe_info = MediaInfo()

    for stream in streams:
        print(stream["codec_type"])
        match stream["codec_type"]:
            case "video":
                
                item = StreamVideo(
                    stream = get_key_with_default(stream, "index"),
                    duration = float(get_key_with_default(stream, "duration")),
                    codec = get_key_with_default(stream, "codec_name"),
                    profile = get_key_with_default(stream, "profile"),
                    bitrate = get_key_with_default(stream, "bit_rate"),

                    width = get_key_with_default(stream, "width"),
                    height = get_key_with_default(stream, "height"),
                    frame_rate = float(simpleeval.simple_eval(get_key_with_default(stream, "avg_frame_rate"))),
                    scan_type = get_key_with_default(stream, "field_order", "unknown"),
                    color_bits = stream["bits_per_raw_sample"],
                    color_model = stream["pix_fmt"],
                    aspect = stream["display_aspect_ratio"].split(":"),
                )

                probe_info.video_streams.append(item)

            case "audio":
                item = StreamAudio()
                item.stream = stream["index"]
                item.duration = float(stream["duration"])
                item.codec = stream["codec_name"]
                item.profile = stream["profile"]
                item.bitrate = stream["bit_rate"]

                item.sample_rate = int(stream["sample_rate"])
                item.channels = int(stream["channels"])
                item.channel_layout = stream["channel_layout"]

            case "subtitle":
                item = StreamText()
                item.stream = stream["index"]
                item.duration = float(stream["duration"])
                item.codec = stream["codec_name"]

                item.start_time = stream["start_time"]

                for k, v in streams["dispositions"]:
                    if v == 1:
                        item.dispositions.append(k)

                item.language = stream["tags"]["language"]

    return probe_info

def get_key_with_default(obj, key, default=None):
    if obj.has_key(key):
        return obj[key]
    else:
        return default


def get_input_streams(job: jobs.StirlingJob):

    streams = job["source"]["info"]["streams"]
    video_stream = job.input_video_stream
    audio_stream = job.input_audio_stream

    if not job.disable_audio:
        if job.input_audio_stream == -1:
            job.input_audio_stream = get_best_audio(
                get_input_streams_from_probe(streams, "audio")
            )
    else:
        if job.input_video_stream == -1:
            job.input_video_stream = get_best_video(
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


def probe(job: jobs.StirlingJob):
    # Check to make sure the appropriate binary files we need are installed.
    assert helpers.check_dependencies_binaries(required_binaries), helpers.log(
        helpers.check_dependencies_binaries(required_binaries)
    )

    # Check if we can probe the input file.
    probe = probe_media_file(job.source)

    job.log("Probed media file: {}".format(str(job.source)))
    job.log("Probe data:", probe)

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
