import json

import args
import helpers

## PLUGIN FUNCTIONS

## Extract Audio Peaks from file
def generate_peaks(job):
    # Peak file Generation options
    # Where to find our extracted WAV file.
    job["commands"]["peaks"]["options"]["i"] = job["commands"]["audio"]["output"]

    # Where to store our calculated audio peaks JSON file.
    output_filename = str(job["output"]["directory"]) + "/annotations/peaks.json"
    job["commands"]["peaks"]["options"]["o"] = output_filename

    jobArgs = args.default_unparser.unparse(**job["commands"]["peaks"]["options"])

    job["commands"]["peaks"]["command"] = "audiowaveform " + jobArgs

    helpers.log(job, "Peak Generation Command: " + job["commands"]["peaks"]["command"])

    job["commands"]["peaks"]["output"] = output_filename
    job["output"]["outputs"].append(output_filename)

    print(json.dumps(job["commands"]["peaks"], indent=4))

    return job
