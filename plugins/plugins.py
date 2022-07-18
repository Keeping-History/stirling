import args
import helpers

## PLUGIN FUNCTIONS

## Generate audio peak/waveform data from file
def generate_peaks(job):
    helpers.log(
        job, "Peak Extract Command: {}".format(job["commands"]["peaks"]["command"])
    )
    return args.default_unparser.unparse(**job["commands"]["peaks"]["options"])


## Generate a Speech-to-text transcription from audio extracted from file
def generate_transcript(job):
    helpers.log(
        job,
        "Transcript Generation Command: {}".format(
            job["commands"]["transcript"]["command"]
        ),
    )
    return args.default_unparser.unparse(
        str(job["output"]["directory"]) + "/source.wav",
        **job["commands"]["transcript"]["options"]
    )
