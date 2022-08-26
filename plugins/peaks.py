import subprocess

from core import args, helpers

required_binaries = ["audiowaveform"]

## PLUGIN FUNCTIONS
## Extract Audio Peaks from file
def generate_peaks(job):
    if not job["arguments"]["disable_peaks"]:
        # Check to make sure the appropriate binary files we need are installed.
        assert helpers.check_dependencies_binaries(required_binaries), helpers.log(
            helpers.check_dependencies_binaries(required_binaries)
        )

        # Peak file Generation options
        # Where to find our extracted WAV file.
        job["commands"]["peaks"]["options"]["i"] = job["commands"]["audio"]["output"]

        # Where to store our calculated audio peaks JSON file.
        output_filename = str(job["output"]["directory"]) + "/annotations/peaks.json"
        job["commands"]["peaks"]["options"]["o"] = output_filename

        jobArgs = args.default_unparser.unparse(**job["commands"]["peaks"]["options"])

        job["commands"]["peaks"]["command"] = "audiowaveform " + jobArgs

        helpers.log(
            job, "Peak Generation Command: " + job["commands"]["peaks"]["command"]
        )

        job["commands"]["peaks"]["output"] = output_filename
        job["output"]["outputs"].append(output_filename)

        # Generate a peak JSON file from the extracted audio file.
        helpers.log(
            job,
            "Generating peak data from audio file '{}' to '{}'".format(
                job["commands"]["peaks"]["options"]["i"],
                job["commands"]["peaks"]["options"]["o"],
            ),
        )
        if not job["arguments"]["simulate"]:
            audio_peak_generation_output = subprocess.getstatusoutput(
                job["commands"]["peaks"]["command"]
            )
            job["output"]["audio_peak_generation"] = audio_peak_generation_output[1]
            helpers.log(
                job,
                "Completed generating peak data from audio file '{}' : '{}'. Command output: {}".format(
                    job["commands"]["peaks"]["options"]["i"],
                    job["commands"]["peaks"]["options"]["o"],
                    helpers.log_string(audio_peak_generation_output[1]),
                ),
            )

    return job
