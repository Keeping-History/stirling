import collections
import json
import uuid
from datetime import datetime
from pathlib import Path

from mergedeep import merge

from core import args, definitions, helpers, video


def create_job_from_template():
    # Start a new job and initialize the job's metadata

    # TODO: Load these from a json template file and provide some simple
    # default command line arguments for common profiles and
    # default settings. The JSON file should be loaded and interpolated
    # with any calculated values.

    job = {
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
            # The directory to output the package. Defaults to a folder named with the job's ID (a random UUID) in the current working folder.
            "output": None,
            # The folder prefix where incoming files are located. Defaults to the current working directory.
            "input_directory": None,
            # Add a prefix to the output directory automatically. Defaults to "output".
            "output_directory_prefix": "output",
            # Delete the temporary incoming source file when finished. By default, the temporary incoming source file is deleted.
            "disable_delete_source": True,
            # When a job is completed, a copy of the video file as it was uploaded is created in the output directory as "source". This can be disabled.
            "disable_source_copy": True,
            # Disables all audio-related tasks. This includes transcripts and peak data generation.
            "disable_audio": False,
            # Disable the transcript extraction.
            "transcript_disable": False,
            # Disable the generation of audio peak data.
            "peaks_disable": False,
            # Disable creating an HLS VOD package.
            "hls_disable": False,
            # Disable creating individual image frames from the input video.
            "disable_frames": False,
            # The encoding profile to use. Defaults to "sd".
            "hls_profile": "sd",
            # In input videos with multiple streams or renditions, specify which one to use. Defaults to the first video stream in the file.
            "input_video_stream": -1,
            # In input videos with multiple streams or renditions, specify which one to use. Defaults to the first video stream in the file.
            "input_audio_stream": -1,
            # The length of each segmented file.
            "hls_segment_duration": 4,
            # The bitrate ratio to use when determining the maximum bitrate for the video.
            "hls_bitrate_ratio": 1.07,
            # The ratio to use when determining the optimum buffer size.
            "hls_buffer_ratio": 1.5,
            # The Constant Rate Factor to use when encoding HLS video. Lower numbers are better quality, but larger files. Defaults to 20. Recommended values are 18-27.
            "hls_crf": 20,
            # The keyframe multiplier. The current framerate is multiplied by this number to determine the number the maximum length before the encoder creates a new one. Defaults to 1.
            "hls_keyframe_multiplier": 1,
            # The number of frames to capture per second. Can be a fraction. Defaults to 1.
            "frames_interval": 1,
            # A debugging option that attempts to setup a full job without actually doing any of the external transcoding/extraction. This should be removed.
            "simulate": False,
            # Enable additional debugging output.
            "debug": True,
            # The Job File, a JSON document that describes the whole job. If it is available, then we will apply it over these defaults.
            "job_file": None,
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
                "args": collections.OrderedDict(
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
                        # Scale the video to the appropriate resolution.
                        "vf": "",
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
                "encoder_profiles": video.EncoderProfiles,
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
            "frames": {
                "command": None,
                "output": None,
                "args": collections.OrderedDict(
                    {
                        # Capture a frame every 1 second of video. Can be a fraction of a second, specified as a float. Default is 1 frame per second.
                        "fps": 1,
                        # Output filename pattern. See ... for more information.
                        "output_filename": "%d.jpg",
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
                        # The input filename
                        "i": "",
                        # Capture a frame ever 1/10 of fps.
                        "r": "{}",
                        # Remove duplicate frames, if necessary
                        "vsync": 0,
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

    return job

def create_job():
    job = definitions.StirlingJob()
    return job

def open_job(job, arguments):
    # Parse arguments cli arguments
    job = args.parse_args(arguments, job)

    # Check to see if aJob JSON file was passed
    # TODO: Update this to use the new job file format
    # if job["arguments"]["job_file"] is not None or job["arguments"]["job_file"] == "":
    #     job_file = Path(job["arguments"]["job_file"])
    #     # Check to make sure the Job JSON file exists
    #     if job_file.is_file():
    #         with open(job_file) as json_file:
    #             # Load the file into our Job Object
    #             new_job = json.load(json_file)
    #             job = merge({}, job, new_job)

    # Make sure we can access our output directory
    job = helpers.get_output_directory(job)

    # Logging
    helpers.log(job, "Starting job")
    helpers.log(job, "Arguments: " + json.dumps(job["arguments"]))
    helpers.log(job, "Output Directory will be: " + str(job["output"]["directory"]))

    # The incoming source file
    job["source"]["input"]["filename"] = job["arguments"]["source"]
    helpers.log(
        job, "File to process will be: " + str(job["source"]["input"]["filename"])
    )

    # Get the incoming file to process
    job = helpers.get_input(job)

    return job


def close_job(job):
    # Close out the job and update its metadata
    job["time_end"] = datetime.now()
    job["duration"] = (job["time_end"] - job["time_start"]).total_seconds()

    # DONE
    helpers.log(
        job,
        "Ending job {} at {}, total duration: {}".format(
            job["id"], job["time_end"], job["duration"]
        ),
    )

    helpers.write_object(job, job["job_file"])
