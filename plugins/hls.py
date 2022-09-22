import pathlib

from core import args, helpers
from plugins import plugins

required_binaries = ["ffmpeg"]

## PLUGIN FUNCTIONS
## Generate an HLS Package from file
def create_rendition(job):
    # Set some holding variables
    renditions_options, encoder_renditions = [], ""

    # Set some variables for easier reading
    encoding_profile = job["commands"]["hls"]["args"]["hls_profile"]

    job["commands"]["hls"]["output_options"]["directory"] = pathlib.Path(
        job["commands"]["hls"]["output_options"]["directory"]
    )

    # Holder for the master m3u8 file contents.
    output_playlist = "#EXTM3U\n#EXT-X-VERSION:3\n"
    helpers.log(job, "Creating renditions.")
    helpers.log(
        job,
        "Profile in use is '{}'.".format(encoding_profile),
    )

    for rendition in job["commands"]["hls"]["encoder_profiles"][encoding_profile]:
        helpers.log(
            job,
            "Creating rendition options for file  {}, rendition {}.".format(
                str(job["commands"]["hls"]["output_options"]["directory"]),
                str(rendition["name"]),
            ),
        )

        output_playlist += (
            "#EXT-X-STREAM-INF:BANDWIDTH={},RESOLUTION={}x{}\n{}.m3u8\n".format(
                int(rendition["bitrate"]) * 1000,
                rendition["width"],
                rendition["height"],
                rendition["name"],
            )
        )

        this_rendition = job["commands"]["hls"]["rendition_options"].copy()
        this_rendition["vf"] = this_rendition["vf"].format(
            rendition["width"], rendition["height"]
        )
        this_rendition["b:v"] = this_rendition["b:v"].format(rendition["bitrate"])
        this_rendition["b:a"] = this_rendition["b:a"].format(rendition["audio-bitrate"])
        this_rendition["maxrate"] = this_rendition["maxrate"].format(
            int(
                float(rendition["bitrate"])
                * job["commands"]["hls"]["args"]["hls_bitrate_ratio"]
            )
        )
        this_rendition["bufsize"] = this_rendition["bufsize"].format(
            int(
                float(rendition["bitrate"])
                * job["commands"]["hls"]["args"]["hls_buffer_ratio"]
            )
        )
        this_rendition["hls_segment_filename"] = this_rendition[
            "hls_segment_filename"
        ].format(
            str(job["commands"]["hls"]["output_options"]["directory"]),
            rendition["name"],
        )
        renditions_options.append(this_rendition)

    return job, renditions_options, encoder_renditions, output_playlist


def create_hls(job):
    if not job["arguments"]["hls_disable"]:
        # Check to make sure the appropriate binary files we need are installed.
        assert helpers.check_dependencies_binaries(required_binaries), helpers.log(
            helpers.check_dependencies_binaries(required_binaries)
        )

        # Create the directory for the hls package.
        hls_output_directory = job["output"]["directory"] / "video" / "hls"
        hls_output_directory.mkdir(parents=True, exist_ok=True)

        # Video encoding options
        # Set the output folder for the HLS segments and playlists. Currently
        # this is the same as the full package output folder, but we're making it a
        # variable here in case we want to change it later.
        # Update our templates with calculated values
        # Calculate the appropriate interval for inserting keyframes.
        try:
            kf_interval = (
                eval(
                    job["source"]["info"]["streams"][
                        job["source"]["input"]["video_stream"]
                    ]["avg_frame_rate"]
                )
                * 2
            )
        except (ValueError, TypeError):
            kf_interval = 60

        # Where to save the HLS output package files.
        job["commands"]["hls"]["output_options"]["directory"] = str(
            hls_output_directory
        )

        # Set the minimum distance between keyframes.
        job["commands"]["hls"]["options"]["keyint_min"] = str(kf_interval)

        # Set the maximum distance between keyframes. Currently, we"re setting this the same as kf_interval.
        job["commands"]["hls"]["options"]["g"] = str(
            kf_interval * job["arguments"]["hls_keyframe_multiplier"]
        )

        # Set the Constant Rate Factor to normalize the bitrate throughout for easier streaming.
        job["commands"]["hls"]["options"]["crf"] = str(job["arguments"]["hls_crf"])

        # Set the length of each h.264 TS segment file.
        job["commands"]["hls"]["options"]["hls_time"] == str(
            job["arguments"]["hls_segment_duration"]
        )

        # The main input file
        job["commands"]["hls"]["input_options"]["i"] = job["source"]["input"][
            "filename"
        ]
        job["commands"]["hls"]["input_options"]["map"] = "0:{}".format(
            str(job["source"]["input"]["video_stream"])
        )

        # The HLS profile to use. See encoder_profiles for more information.
        job["commands"]["hls"]["args"]["hls_profile"] == str(
            job["arguments"]["hls_profile"]
        )

        # These two values help us fine-tune the HLS encoding.
        job["commands"]["hls"]["args"]["hls_bitrate_ratio"] == str(
            job["arguments"]["hls_bitrate_ratio"]
        )
        job["commands"]["hls"]["args"]["hls_buffer_ratio"] == str(
            job["arguments"]["hls_buffer_ratio"]
        )

        # Create template entries for each of the encoder renditions specified in the profile.
        job, renditions_options, encoder_renditions, output_playlist = create_rendition(
            job
        )

        for rendition_option in renditions_options:
            encoder_renditions += " " + args.default_unparser.unparse(
                **(job["commands"]["hls"]["options"] | rendition_option)
            )

        # Fix unargparsers insistence on "deciding" which types of quotes to use.
        encoder_renditions = encoder_renditions.replace("'", '"')

        job["commands"]["hls"]["command"] = "ffmpeg " + (
            args.ffmpeg_unparser.unparse(
                **(
                    job["commands"]["hls"]["cli_options"]
                    | job["commands"]["hls"]["input_options"]
                )
            )
            + " "
            + encoder_renditions
        )

        helpers.log(job, "HLS Encoding Command: " + job["commands"]["hls"]["command"])

        # Convert the video file to packaged HLS.
        helpers.log(
            job,
            "Generating HLS package from source file '{}' to directory '{}'".format(
                job["commands"]["hls"]["input_options"]["i"],
                str(job["commands"]["hls"]["output_options"]["directory"]),
            ),
        )

        # Create an m3u8 file to hold all the renditions.
        job = create_master_playlist(job, output_playlist)

        job["output"]["video_hls_generation"] = plugins.do(
            job["commands"]["hls"]["command"], job["arguments"]["simulate"]
        )
        helpers.log(
            job,
            "Created HLS video package in {0}".format(
                str(job["commands"]["hls"]["output_options"]["directory"])
            ),
        )

        job["output"]["outputs"].append(
            job["commands"]["hls"]["output_options"]["directory"]
        )

    return job


def create_master_playlist(job, output_playlist):
    playlist = str(
        job["commands"]["hls"]["output_options"]["directory"] / "playlist.m3u8"
    )
    # Create an m3u8 file to hold all the renditions.
    helpers.log(
        job,
        "Creating m3u8 playlist file {0}".format(playlist),
    )
    if not job["arguments"]["simulate"]:
        m3u8_file = open(
            playlist,
            "w",
        )
        m3u8_file.write(output_playlist)
        m3u8_file.close()

        helpers.log(
            job,
            "Created m3u8 playlist file {0}".format(playlist),
        )

        job["output"]["outputs"].append(
            job["commands"]["hls"]["output_options"]["directory"] / "playlist.m3u8"
        )

    return job
