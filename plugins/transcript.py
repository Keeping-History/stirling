import subprocess
from dataclasses import dataclass

from core import args, definitions, helpers

# Specify the required binaries in a list.
required_binaries = ["autosub"]


@dataclass
class StirlingArgsPluginTranscript(definitions.StirlingClass):
    """StirlingArgsPluginTranscript are for creating speech-to-text transcripts.
    These transcripts can be used as-is, or can be used later for
    confidence training, language analysis or for adding other contexts."""

    # Disable the transcript extraction.
    transcript_disable: bool = False


## PLUGIN FUNCTIONS
## Extract Audio Peaks from file
def generate_transcript(job):
    # Plugins receive the job object.

    # Check to see if we can run this plugin.
    if not job["arguments"]["transcript_disable"]:

        # Check to make sure the appropriate binary files we need are installed.
        assert helpers.check_dependencies_binaries(required_binaries), helpers.log(
            helpers.check_dependencies_binaries(required_binaries)
        )

        # Peak file Generation options

        # Where to store our calculated audio peaks JSON file.
        output_filename = (
            str(job["output"]["directory"]) + "/annotations/subtitles.json"
        )
        job["commands"]["transcript"]["options"]["o"] = output_filename

        # Unparse our command line arguments, from our job object, into a string.
        jobArgs = args.default_unparser.unparse(
            job["commands"]["audio"]["output"],
            **job["commands"]["transcript"]["options"]
        )

        # Create the command to run.
        job["commands"]["transcript"]["command"] = "autosub " + jobArgs
        helpers.log(
            job,
            "Transcript Generation Command: "
            + job["commands"]["transcript"]["command"],
        )

        # Add the output of the plugin to the job.
        job["commands"]["transcript"]["output"] = output_filename
        job["output"]["outputs"].append(output_filename)

        # Run the command to generate transcript from the extracted audio.
        helpers.log(
            job,
            "Generating transcript data from audio file '{}' to {}".format(
                job["commands"]["peaks"]["options"]["i"],
                job["commands"]["transcript"]["output"],
            ),
        )

        if not job["arguments"]["simulate"]:
            generate_transcript_output = subprocess.getstatusoutput(
                job["commands"]["transcript"]["command"]
            )

            # Get the output of the command and add it to the job.
            job["output"]["transcript_generation"] = generate_transcript_output[1]
            helpers.log(
                job,
                "Completed generating transcript data from audio file '{}' to '{}'. Command output: {}".format(
                    job["commands"]["peaks"]["options"]["i"],
                    job["commands"]["transcript"]["output"],
                    generate_transcript_output[1],
                ),
            )

    # Plugins should always return the job.
    return job
