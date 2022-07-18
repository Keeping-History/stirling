import argparse

import argunparse

default_unparser = argunparse.ArgumentUnparser(long_opt="-", opt_value=" ")
autosub_unparser = argunparse.ArgumentUnparser(long_opt="--", opt_value="=")
ffmpeg_unparser = argunparse.ArgumentUnparser(
    long_opt="-", opt_value=" ", begin_delim="", end_delim=""
)


def parse_args(args, job):
    parser = argparse.ArgumentParser(
        description="Package a media file for \
                                                analysis and streaming."
    )

    parser.add_argument(
        "source", metavar="I", type=str, nargs="?", help="The input media file."
    )
    parser.add_argument(
        "output",
        metavar="O",
        type=str,
        nargs="?",
        default=None,
        help="The directory to output the package. \
                            Defaults to a folder named with the job's ID \
                            (a random UUID) in the current working folder.",
    )

    parser.add_argument(
        "--input-directory",
        type=str,
        required=False,
        default="",
        help="The folder prefix where incoming files are located. \
                            Defaults to the current working directory.",
    )
    parser.add_argument(
        "--output-directory-prefix",
        type=str,
        required=False,
        default="output",
        help='Add a prefix to the output directory \
                            automatically. Defaults to "output".',
    )

    parser.add_argument(
        "--disable-delete-source",
        action="store_true",
        default=True,
        help="Delete the temporary incoming source file when \
                            finished. By default, the temporary incoming \
                            source file is deleted.",
    )
    parser.add_argument(
        "--disable-source-copy",
        action="store_true",
        default=False,
        help='When a job is completed, a copy of the video file \
                            as it was uploaded is created in the output \
                            directory as "source". This can be disabled.',
    )

    parser.add_argument(
        "--disable-audio",
        action="store_true",
        default=False,
        help="Disables all audio-realted tasks. This includces \
                            transcripts and peak data generation.",
    )
    parser.add_argument(
        "--disable-transcript",
        action="store_true",
        default=False,
        help="Disable the transcript extraction.",
    )
    parser.add_argument(
        "--disable-peaks",
        action="store_true",
        default=False,
        help="Disable the generation of audio peak data.",
    )
    parser.add_argument(
        "--disable-hls",
        action="store_true",
        default=False,
        help="Disable creating an HLS VOD package.",
    )

    # The video encoding profile to use. The default is "sd" which is a standard
    # defintion profile suitable for most SD, low-quality, 4:3 video.
    parser.add_argument(
        "--hls-profile",
        type=str,
        required=False,
        default="sd",
        help='The encoding profile to use. Defaults to "sd".',
    )

    # Options for the input file
    parser.add_argument(
        "--input-video-stream",
        type=int,
        required=False,
        default=-1,
        help="In input videos with multiple streams or renditions, \
                            specify which one to use. Defaults to the first video \
                            stream in the file.",
    )
    parser.add_argument(
        "--input-audio-stream",
        type=int,
        required=False,
        default=-1,
        help="In input videos with multiple streams or renditions, \
                            specify which one to use. Defaults to the first video \
                            stream in the file.",
    )

    # HLS specific options for the output
    parser.add_argument(
        "--hls-segment-duration",
        type=int,
        required=False,
        default=4,
        help="The length of each segmented file.",
    )
    parser.add_argument(
        "--hls-bitrate-ratio",
        type=int,
        required=False,
        default=1.07,
        help="The bitrate ratio to use when determining the maximum \
                            bitrate for the video.",
    )
    parser.add_argument(
        "--hls-buffer-ratio",
        type=int,
        required=False,
        default=1.5,
        help="The ratio to use when determining the optimum buffer size.",
    )
    parser.add_argument(
        "--hls-crf",
        type=int,
        required=False,
        default=20,
        help="The Constant Rate Factor to use when encoding HLS \
                            video. Lower numbers are better quality, but larger \
                            files. Defaults to 20. Recommended values are 18-27.",
    )
    parser.add_argument(
        "--hls-keyframe-multiplier",
        type=int,
        required=False,
        default=1,
        help="The keyframe multipler. The current framerate is multiplied \
                            by this number to determine the number the maximum \
                            length before the encoder creates a new one. \
                            Defaults to 1.",
    )

    # Misc options
    parser.add_argument(
        "--simulate",
        action="store_true",
        default=False,
        help="A debugging option that attempts to setup a full \
                            job without actually doing any of the external \
                            transcoding/extraction. This should be removed.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=True,
        help="Enable additional debugging output.",
    )

    parsedArgs = parser.parse_args(args)

    # If we've disabled audio, also disable transcripts and peak generation.
    if parsedArgs.disable_audio:
        parsedArgs.disable_transcript, parsedArgs.disable_peaks = True, True

    # Set a streams for simulation mode
    if parsedArgs.simulate:
        parsedArgs.input_video_stream = 0
        parsedArgs.input_audio_stream = 1

    # Put our arguments in our job    return(dict2.update(dict1))
    job["info"]["arguments"] = {**job["info"]["arguments"], **vars(parsedArgs)}

    return job
