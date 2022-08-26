import subprocess

from core import args, helpers

required_binaries = ["ffmpeg"]

## PLUGIN FUNCTIONS
# TODO: Extract iFrames to jpgs.
# ##### -f image2 -vf "select=gt(scene\,0.5), -vsync vfr yosemiteThumb%03d.png  (scene change)
# ##### -f image2 -vf "select=eq(pict_type\,PICT_TYPE_I)"  -vsync vfr yi%03d.png (for every iFrame)
# ##### -f image2 -vf fps=fps=1/10 ythumb%3d.png (period thumbnails)
# ##### -f image2 -ss 00:00:18.123 -frames:v 1 yosemite.png (specific time)
# ##### ffmpeg -i source -vf fps=1,select='not(mod(t,5))' -vsync 0 -frame_pts 1 z%d.jpg

## Extract Audio from file
def extract_frames(job):
    if not job["arguments"]["disable_frames"]:
        # Check to make sure the appropriate binary files we need are installed.
        assert helpers.check_dependencies_binaries(required_binaries), helpers.log(
            helpers.check_dependencies_binaries(required_binaries)
        )

        #### Some helper variables
        # Input Filename
        input_filename = job["source"]["input"]["filename"]
        # Create the directory for the images.
        frames_output_directory = job["output"]["directory"] / "img" / "frames"
        output_filename = (
            frames_output_directory
            / job["commands"]["frames"]["args"]["output_filename"]
        )
        fps = job["commands"]["frames"]["options"]["vf"].format(
            job["commands"]["frames"]["args"]["fps"],
        )

        # Frame extraction options
        # Where to save the image files.
        job["commands"]["hls"]["output_options"]["directory"] = frames_output_directory

        # The input video file
        job["commands"]["frames"]["options"]["i"] = input_filename

        # The number of frames to capture for each second of video.
        job["commands"]["frames"]["options"]["vf"] = fps

        jobArgs = args.default_unparser.unparse(
            *{output_filename},
            **(
                job["commands"]["frames"]["cli_options"]
                | job["commands"]["frames"]["options"]
            )
        )

        job["commands"]["frames"]["command"] = "ffmpeg " + jobArgs

        helpers.log(
            job,
            "Frames Extract Command: {}".format(job["commands"]["frames"]["command"]),
        )

        job["commands"]["frames"]["output"] = frames_output_directory
        job["output"]["outputs"].append(frames_output_directory)

        # Extract frames from video file
        helpers.log(
            job,
            "Extracting image frames from video file '{}' to '{}'".format(
                job["source"]["input"]["filename"],
                job["commands"]["frames"]["output"],
            ),
        )

        if not job["arguments"]["simulate"]:
            # Create the output directory
            frames_output_directory.mkdir(parents=True, exist_ok=True)

            # Run the command
            command_output = subprocess.getstatusoutput(
                job["commands"]["frames"]["command"]
            )
            job["output"]["frames_extract"] = command_output[1]

            helpers.log(
                job,
                "Completed extracting images from video file '{}' to '{}'. Command output: {}".format(
                    job["source"]["input"]["filename"],
                    job["commands"]["frames"]["output"],
                    helpers.log_string(command_output[1]),
                ),
            )

    return job
