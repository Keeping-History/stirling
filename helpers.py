import collections
import json
import os
import pathlib
import shutil
import sys
import uuid
from datetime import datetime

import requests
import validators

import args
import helpers


def create_job_from_template():
    # Start a new job and initize the job's metadata

    # TODO: Load these from a json template file and provide some simple
    # default command line arguments for common profiles and
    # default settings. The JSON file should be loaded and interpolated
    # with any calculated values.

    job = {
        "info": {
            # The ID of the job. We create a random UUID whenever a job is
            # created, however a custom one can be supplied so long as it
            # is globally unique.
            "id": str(uuid.uuid4()),
            # The start time of the job, as a datetime.datetime object in UTC.
            "time_start": datetime.now(),
            # The end time of the job, as a datetime.datetime object in UTC.
            "time_end": None,
            # The duration of the job, in seconds.
            "duration": None,
            # The location of the job log file.
            "log_file": None,
            # The location of the JSON job file.
            "job_file": None,
            # Command line arguments.
            "arguments": {
                "source": None,
                "output": None,
                "input_directory": None,
                "output_directory_prefix": "output",
                "disable_delete_source": True,
                "disable_source_copy": False,
                "disable_audio": False,
                "disable_transcript": False,
                "disable_peaks": False,
                "disable_hls": False,
                "hls_profile": "1080p-high",
                "input_video_stream": -1,
                "input_audio_stream": -1,
                "hls_segment_duration": 4,
                "hls_bitrate_ratio": 1.07,
                "hls_buffer_ratio": 1.5,
                "hls_crf": 20,
                "hls_keyframe_multiplier": 1,
                "simulate": False,
                "debug": True,
            },
        },
        "output": {
            # The output directory for the package and its contents
            "directory": None,
            # Specific output files/directories generated are put here
            "outputs": [],
        },
        "commands": {
            "hls": {
                # The final, completed command that is run.
                "command": None,
                # The output from the command above
                "output": None,
                "hls_args": collections.OrderedDict(
                    {
                        # The encoder profile to use. The default is "sd" which
                        # is a standard def package
                        "hls_profile": "sd",
                        "hls_bitrate_ratio": 1,
                        "hls_buffer_ratio": 1,
                    }
                ),
                # A set of input options for the encoder.
                "input_options": collections.OrderedDict(
                    {
                        # The source (input) file
                        "i": None,
                        # The stream to use for the input. For more information
                        # se https://trac.ffmpeg.org/wiki/Map
                        "map": None,
                    }
                ),
                "output_options": collections.OrderedDict(
                    {
                        # The output directory for the HLS package.
                        "directory": None,
                    }
                ),
                "cli_options": collections.OrderedDict(
                    {
                        # Hide ffmpeg"s console banner output.
                        "hide_banner": True,
                        # Tell ffmpeg to just agree to whatever
                        "y": True,
                        # Output log level. See here for more on loglevels:
                        # https://ffmpeg.org/ffmpeg.html#Generic-options
                        "loglevel": "debug",
                    }
                ),
                "options": collections.OrderedDict(
                    {
                        # Audio codec to encode with. We prefer AAC over mp3.
                        "acodec": "aac",
                        # Audio sample rate to encode with. Default is the same as the source.
                        "ar": "44100",
                        # Video codec to encode with. H264 is the most common and our preferred codec for compatibility purposes.
                        "vcodec": "h264",
                        # Video encoding profile, set to a legacy setting for compatibility.
                        "profile:v": "main",
                        # The CRF value to use when encoding HLS video, lower is better
                        # quality. A "sane" value is 17-28. Default is 20. Currently, we are using
                        # args for this, but it is here to represent the template for future use.
                        "crf": "20",
                        # Adjusts the sensitivity of x264's scenecut detection. Rarely needs to be adjusted. 0 disables scene detection. Recommended default: 40
                        "sc_threshold": "40",
                        # Set the Group Picture Size (GOP). Default is 12.
                        "g": "12",
                        # Set the minimum distance between keyframes.
                        "keyint_min": "25",
                        # The target length of each segmented file. Default is 2.
                        "hls_time": "2",
                        # The type of HLS playlist to create.
                        "hls_playlist_type": "vod",
                        # Enable faster file streaming start for HLS files by moving some of the metadata to the beginning of the file after transcode.
                        "movflags": "+faststart",
                        # Audio codec to encode with. We prefer AAC over mp3.
                        "vf": "",  # Scale the video to the appropriate resolution.
                        "b:v": "",
                        # Set the maximum video bitrate.
                        "maxrate": "",
                        # Set the size of the buffer before ffmpeg recalculates the bitrate.
                        "bufsize": "",
                        # Set the audio output bitrate.
                        "b:a": "",
                    }
                ),
                "rendition_options": collections.OrderedDict(
                    {
                        # Scale the video to the appropriate resolution. A default string template is provided to input the width and height.
                        "vf": "scale=w={}:h={}:force_original_aspect_ratio=decrease",
                        # Control the bitrate. A default string template is provided.
                        "b:v": "{}k",
                        # Set the maximum video bitrate. A default string template is provided.
                        "maxrate": "{0}k",
                        # Set the size of the buffer before ffmpeg recalculates the bitrate. A default string template is provided.
                        "bufsize": "{0}k",
                        # Set the audio output bitrate. A default string template is provided.
                        "b:a": "{0}k",
                        # Set the output filename for the HLS segment. A default string template is provided.
                        "hls_segment_filename": "{0}/{1}_%09d.ts' '{0}/{1}.m3u8",
                    }
                ),
            },
            "transcript": {
                "command": None,
                "output": None,
                "options": collections.OrderedDict(
                    {
                        # The output filename for the transcript.
                        "o": None,
                        # Output transcript file language. Default to English.
                        "D": "en",
                        # Source file language to transcribe. Default to English.
                        "S": "en",
                        # Number of concurrent API calls.
                        "C": "10",
                        # Output transcript file format. Defaults to JSON.
                        "F": "json",
                        # A Google Translate API key. This is needed when the language of the source and destination do not match. The default is blank, which uses a Google Chrome/Android System access key.
                        # ["api-key", "aaa"],
                    }
                ),
            },
            "peaks": {
                "command": None,
                "output": None,
                "options": collections.OrderedDict(
                    {
                        # The WAV input filename
                        "i": None,
                        # The output JSON/TXT filename
                        "o": None,
                    }
                ),
            },
            "audio": {
                "command": None,
                "output": None,
                "cli_options": collections.OrderedDict(
                    {
                        # Hide ffmpeg"s console banner output.
                        "hide_banner": True,
                        # Tell ffmpeg to just agree to whatever
                        "y": True,
                        # Output log level. See here for more on loglevels:
                        # https://ffmpeg.org/ffmpeg.html#Generic-options
                        "loglevel": "debug",
                    }
                ),
                "options": collections.OrderedDict(
                    {
                        # The input filename
                        "i": "",
                        # Extract only one audio track.
                        "ac": "1",
                        # Encode as a PCM waveform file.
                        "acodec": "pcm_s16le",
                        # Sample rate of the PCM waveform file.
                        "ar": "44800",
                    }
                ),
            },
            "thumbnails": {
                "command": None,
                "output": None,
                "cli_options": collections.OrderedDict(
                    {
                        # Hide ffmpeg"s console banner output.
                        "hide_banner": True,
                        # Tell ffmpeg to just agree to whatever
                        "y": True,
                        # Output log level. See here for more on loglevels:
                        # https://ffmpeg.org/ffmpeg.html#Generic-options
                        "loglevel": "debug",
                    }
                ),
                "options": collections.OrderedDict(
                    {
                        # The input filename
                        "i": "",
                        # Extract only one audio track.
                        "f": "image2",
                        # Capture a frame ever 1/10 of fps.
                        "vf": "fps=fps=1/10",
                    }
                ),
            },
        },
        "source": {
            # Here is stored info from ffprobe about the source file and it's contents
            "info": {},
            "input": {
                # The input filename. Can be a full path.
                "filename": None,
                # The index of the video stream
                "video_stream": None,
                # The index of the audio stream
                "audio_stream": None,
            },
        },
    }

    # Parse arguments and setup "unparsers" to setup cli jobs(())
    job = args.parse_args(sys.argv[1:], job)

    return job


def open_job(job):
    job = get_output_directory(job)
    helpers.log(job, "Starting job")
    helpers.log(job, "Arguments: " + json.dumps(job["info"]["arguments"]))
    helpers.log(job, "Output Directory will be: " + str(job["output"]["directory"]))

    # The incoming source file
    job["source"]["input"]["filename"] = job["info"]["arguments"]["source"]
    helpers.log(
        job, "File to process will be: " + str(job["source"]["input"]["filename"])
    )

    # Get the incoming file to process
    job = helpers.get_input(job)

    return job


def close_job(job):
    # Close out the job and update its metadata
    job["info"]["time_end"] = datetime.now()
    job["info"]["duration"] = (
        job["info"]["time_end"] - job["info"]["time_start"]
    ).total_seconds()
    return job


def write_object(obj, filename):
    # Write the object to a file
    output_file = open(filename, "w")
    output_file.write(json.dumps(obj, indent=4, default=str))
    output_file.close()


def check_dependencies_binaries(required_binaries):
    required_binaries_missing = []
    for program in required_binaries:
        if shutil.which(program) is None:
            required_binaries_missing.append(program)
    if not len(required_binaries_missing) == 0:
        return "missing binary dependencies: {}".format(
            " ".join(required_binaries_missing)
        )
    return True


def get_input(job):
    source = job["source"]["input"]["filename"]
    output = job["output"]["directory"]
    disable_delete_source = job["info"]["arguments"]["disable_delete_source"]
    disable_source_copy = job["info"]["arguments"]["disable_source_copy"]

    # Get a full path to name our source file when we move it. We'll use this
    # value later on as an input filename for specific commands.
    incoming_filename = str(output) + "/source" + pathlib.Path(source).suffix

    # If the incoming source is a URL, then let's download it.
    if validators.url(source):
        response = requests.get(source)
        open(incoming_filename, "wb").write(response.content)
    else:
        if not disable_source_copy:
            # Unless this is a simulation or we explicitly disabled it, copy the source
            # file to the output directory as 'source'
            shutil.copyfile(pathlib.Path(source).absolute(), incoming_filename)
            if not disable_delete_source:
                os.remove(source)
        else:
            incoming_filename = source

    job["source"]["input"]["filename"] = pathlib.Path(incoming_filename)
    return job


def get_output_directory(job):
    output = job["info"]["arguments"]["output"]
    prefix = job["info"]["arguments"]["output_directory_prefix"]

    # Check arguments and set any appropriate calculated defaults.
    # The output directory. If not specified, then create one using the job_id.
    if job["info"]["arguments"]["output_directory_prefix"] is not None:
        prefix = "/" + str(prefix)
    if job["info"]["arguments"]["output"] is None:
        output_directory = pathlib.Path(os.getcwd() + prefix + "/" + job["info"]["id"])
    else:
        output_directory = pathlib.Path(prefix + output)

    # Make the output directory, if it doesn't exist.
    if not output_directory.is_dir():
        output_directory.mkdir(parents=True, exist_ok=True)
        output_directory = pathlib.Path(output_directory)
        annotations_output_directory = output_directory / "annotations"
        hls_output_directory = output_directory / "hls"
        annotations_output_directory.mkdir(parents=True, exist_ok=True)
        hls_output_directory.mkdir(parents=True, exist_ok=True)

    job["output"]["directory"] = output_directory
    job["info"]["log_file"] = job["output"]["directory"] / "job.log"
    job["info"]["job_file"] = job["output"]["directory"] / "job.json"

    # Make sure we have a directory for the output files
    assert job["output"]["directory"].is_dir(), helpers.log(
        job,
        "could not find the path {} for output files".format(
            str(job["output"]["directory"])
        ),
    )

    # Make sure we can write to the directory for the output files
    assert os.access(str(job["output"]["directory"]), os.W_OK), helpers.log(
        "could not write to path {} for output files".format(
            str(job["output"]["directory"])
        )
    )

    return job


def log(job, message, debug=True):
    stamp = datetime.now()
    duration = str((stamp - job["info"]["time_start"]).total_seconds() * 1000)
    line_header = "[{}] [+{}] [{}]".format(
        stamp.strftime("%Y-%m-%d %H:%M:%S"), duration + "ms", job["info"]["id"]
    )

    if debug:
        print("{}: {}\n".format(line_header, message))

    file1 = open(job["info"]["log_file"], "a")  # append mode
    file1.write("{}: {}\n".format(line_header, message))
    file1.close()


def log_object(object, line_identifier="+", header="", indent=4):
    print(type(object))
    return log_string(
        header + json.dumps(vars(object), indent=indent), line_identifier, indent
    )


def log_string(string, line_identifier="+", indent=4):
    new_line_string = "\n" + line_identifier + " " * indent
    return new_line_string + new_line_string.join(string.splitlines())
