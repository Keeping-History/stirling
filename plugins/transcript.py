import args
import helpers

## PLUGIN FUNCTIONS

## Extract Audio Peaks from file
def generate_transcript(job):
    # Peak file Generation options

    # Where to store our calculated audio peaks JSON file.
    output_filename = str(job["output"]["directory"]) + "/annotations/subtitles.json"
    job["commands"]["transcript"]["options"]["o"] = output_filename

    jobArgs = args.default_unparser.unparse(
        job["commands"]["audio"]["output"], **job["commands"]["transcript"]["options"]
    )

    job["commands"]["transcript"]["command"] = "autosub " + jobArgs

    helpers.log(
        job,
        "Transcript Generation Command: " + job["commands"]["transcript"]["command"],
    )

    job["commands"]["transcript"]["output"] = output_filename
    job["output"]["outputs"].append(output_filename)

    return job
