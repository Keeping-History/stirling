import subprocess

import helpers
import probe
import requirements
from plugins import audio, hls, peaks, transcript

# TODO: Add support for multiple audio tracks.
# TODO: Add support for multiple transcripts/languages
# TODO: Extract iFrames from video into playlist.
# TODO: Extract iFrames to jpgs.
# ##### ffmpeg -i yosemiteA.mp4 -vf  "select=gt(scene\,0.5), scale=640:360" -vsync vfr yosemiteThumb%03d.png  (scene change)
# ##### ffmpeg -i yosemiteA.mp4 -f image2 -vf "select=eq(pict_type\,PICT_TYPE_I)"  -vsync vfr yi%03d.png (for every iFrame)
# ##### ffmpeg -i yosemiteA.mp4 -f image2 -vf fps=fps=1/10 ythumb%3d.png (period thumbnails)
# ##### ffmpeg -i yosemiteA.mp4 -ss 00:00:18.123 -frames:v 1 yosemite.png (specific time)

# TODO: Revisit https://github.com/kkroening/ffmpeg-python/tree/master/ffmpeg for argument creation

# BEGIN
# Create our job dictionary that will store all the information
# about the job and ceate a timestamp of when we started this job,
# and create a unique UUID to identify this job, the output file,
# and the output directory (when not specified explicitly).
job = helpers.create_job_from_template()

# Get the output directory
job = helpers.open_job(job)

# VALIDATIONS

# Ensure the proper binaries are installed.
assert helpers.check_dependencies_binaries(requirements.required_binaries), helpers.log(
    helpers.check_dependencies_binaries(requirements.required_binaries)
)

job = probe.probe(job)
job = audio.extract_audio(job)


job = peaks.generate_peaks(job)
job = transcript.generate_transcript(job)
job = hls.create_hls(job)

job["output"]["outputs"] = [
    job["commands"]["peaks"]["options"]["o"],
    job["commands"]["transcript"]["output"],
    job["commands"]["hls"]["output_options"]["directory"],
]

# TODO: We need to create a separate ffmpeg call with the lowest quality settings
# at the source files resolution for previewing and fast editor preview.

# COMMANDS
# The following creates the necessary parameters for the commands we need to
# run. We're going to create command line args for each of the hls profile's
# encoder renditions.


helpers.log(job, "Transcript Command: " + job["commands"]["transcript"]["command"])
helpers.log(job, "HLS Encoding Command: " + job["commands"]["hls"]["command"])

if not job["info"]["arguments"]["disable_audio"]:
    # Extract audio from video file
    if not job["info"]["arguments"]["simulate"]:
        helpers.log(
            job,
            "Extracting audio from video file '{}' to '{}'".format(
                job["source"]["input"]["filename"],
                job["commands"]["audio"]["output"],
            ),
        )
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

    if not job["info"]["arguments"]["disable_peaks"]:
        # Generate a peak JSON file from the extracted audio file.
        helpers.log(
            job,
            "Generating peak data from audio file '{}' to '{}'".format(
                job["commands"]["peaks"]["options"]["i"],
                job["commands"]["peaks"]["options"]["o"],
            ),
        )
        if not job["info"]["arguments"]["simulate"]:
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

    if not job["info"]["arguments"]["disable_transcript"]:
        # Generate a transcript/subtitles from the extracted audio.
        helpers.log(
            job,
            "Generating transcript data from audio file '{}' to {}".format(
                job["commands"]["peaks"]["options"]["i"],
                job["commands"]["transcript"]["output"],
            ),
        )
        if not job["info"]["arguments"]["simulate"]:
            generate_transcript_output = subprocess.getstatusoutput(
                job["commands"]["transcript"]["command"]
            )
            job["output"]["transcript_generation"] = generate_transcript_output[1]
            helpers.log(
                job,
                "Completed generating transcript data from audio file '{}' to '{}'. Command output: {}".format(
                    job["commands"]["peaks"]["options"]["i"],
                    job["commands"]["transcript"]["output"],
                    generate_transcript_output[1],
                ),
            )

if not job["info"]["arguments"]["disable_hls"]:
    # Convert the video file to packaged HLS.
    helpers.log(
        job,
        "Generating HLS package from source file '{}' to directory '{}'".format(
            job["commands"]["hls"]["input_options"]["i"],
            str(job["commands"]["hls"]["output_options"]["directory"]),
        ),
    )
    if not job["info"]["arguments"]["simulate"]:
        video_hls_generation_output = subprocess.getstatusoutput(
            job["commands"]["hls"]["command"]
        )
        job["output"]["video_hls_generation"] = video_hls_generation_output[1]
        helpers.log(
            job,
            "Created HLS video package in {0}".format(
                str(job["commands"]["hls"]["output_options"]["directory"])
            ),
        )


job = helpers.close_job(job)
helpers.write_object(job, job["info"]["job_file"])

# DONE
helpers.log(
    job,
    "Ending job {} at {}, total duration: {}".format(
        job["info"]["id"], job["info"]["time_end"], job["info"]["duration"]
    ),
)


# MOVE EVERYTHING ABOVE INTO FUNCTIONS AND CALL THE MAIN LIKE SO
# if __name__ == '__main__':
#     Do stuff
