import json
import subprocess
import sys

import helpers


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

    streams, video_stream, audio_stream, disable_hls = (
        job["source"]["info"]["streams"],
        job["info"]["arguments"]["input_video_stream"],
        job["info"]["arguments"]["input_audio_stream"],
        job["info"]["arguments"]["disable_hls"],
    )

    if disable_hls:
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

    print("best video stream")
    print(v, max(v, key=v.get))
    return max(v, key=v.get)


def get_best_audio(probe_streams):
    if len(probe_streams) > 0:
        a = {}
        for stream in probe_streams:
            a[stream[0]] = [stream[1].get("bit_rate")]

    print("best audio stream")
    print(a, max(a, key=a.get))
    return max(a, key=a.get)


def probe(job):
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
