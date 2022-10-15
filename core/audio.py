import subprocess
from dataclasses import dataclass

from core import definitions

from core import args, helpers

required_binaries = ["ffmpeg"]

@dataclass
class StirlingPluginAudio(definitions.StirlingClass):
    """StirlingPluginAudio are for using a source audio-only file or for
    extracting audio from a video file."""

    # In input videos with multiple streams or renditions, specify which one to
    # use. Defaults to the first video stream in the file.
    source_audio_stream: int = -1
    # Disables all audio-related tasks. This includes transcripts and peak data
    # generation.
    disable_audio: bool = False

## PLUGIN FUNCTIONS

## Extract Audio from file
def extract_audio(job):
    if not job["arguments"]["disable_audio"]:
        # Check to make sure the appropriate binary files we need are installed.
        assert helpers.check_dependencies_binaries(required_binaries), helpers.log(
            helpers.check_dependencies_binaries(required_binaries)
        )

        # WAV extraction options
        # Where to store our extracted audio file.
        job["commands"]["audio"]["options"]["i"] = job["source"]["input"]["filename"]
        job["commands"]["audio"]["options"]["map"] = "0:{}".format(
            str(job["source"]["input"]["audio_stream"])
        )

        output_filename = str(job["output"]["directory"]) + "/source.wav"

        jobArgs = args.default_unparser.unparse(
            *{output_filename},
            **(
                job["commands"]["audio"]["cli_options"]
                | job["commands"]["audio"]["options"]
            )
        )

        job["commands"]["audio"]["command"] = "ffmpeg " + jobArgs

        helpers.log(
            job, "Audio Extract Command: {}".format(job["commands"]["audio"]["command"])
        )

        job["commands"]["audio"]["output"] = output_filename
        job["output"]["outputs"].append(output_filename)

        # Extract audio from video file
        helpers.log(
            job,
            "Extracting audio from video file '{}' to '{}'".format(
                job["source"]["input"]["filename"],
                job["commands"]["audio"]["output"],
            ),
        )

        if not job["arguments"]["simulate"]:
            audio_extract_output = subprocess.getstatusoutput(
                job["commands"]["audio"]["command"]
            )

            job["output"]["audio_extract"] = audio_extract_output[1]

            helpers.log(
                job,
                "Completed extracting audio from video file '{}' to '{}'. Command output: {}".format(
                    job["source"]["input"]["filename"],
                    job["commands"]["audio"]["output"],
                    helpers.log_string(audio_extract_output[1]),
                ),
            )

    return job
