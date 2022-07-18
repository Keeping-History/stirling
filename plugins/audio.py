import args
import helpers

## PLUGIN FUNCTIONS

## Extract Audio from file
def extract_audio(job):
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

    return job
