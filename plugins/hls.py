import collections
import pathlib
from dataclasses import dataclass, field

from core import args, definitions, helpers, jobs
from plugins import plugins

required_binaries = ["ffmpeg"]


@dataclass
class StirlingPluginHLS(definitions.StirlingClass):
    """StirlingPluginHLS is for creating an HLS VOD streaming package from
    the input source video."""

    _plugin_name: str = "hls"

    video_source_stream: int = -1
    audio_source_stream: int = -1

    # Disable creating an HLS VOD package.
    hls_disable: bool = False
    # The encoding profile to use. Defaults to "sd".
    hls_profile: str = "sd"
    # The length of each segmented file.
    hls_segment_duration: int = 4
    # The bitrate ratio to use when determining the maximum bitrate for the
    # video.
    hls_bitrate_ratio: float = 1.07
    # The ratio to use when determining the optimum buffer size.
    hls_buffer_ratio: float = 1.5
    # The Constant Rate Factor to use when encoding HLS video. Lower numbers are
    # better quality, but larger files. Defaults to 20. Recommended values are
    # 18-27.
    hls_crf: int = 20
    # The keyframe multiplier. The current framerate is multiplied by this
    # number to determine the number the maximum length before the encoder
    # creates a new one. Defaults to 1.
    hls_keyframe_multiplier: int = 1
    # Audio codec to encode with. We prefer AAC over mp3.
    hls_audio_codec: str = "aac"
    # Audio sample rate to encode with. Default is the same as the source.
    hls_audio_sample_rate: int = 0
    # Video codec to encode with. H264 is the most common and our preferred
    # codec for compatibility purposes.
    hls_video_codec: str = "h264"
    # Video encoding profile, set to a legacy setting for compatibility.
    hls_video_profile: str = "main"
    # Adjusts the sensitivity of the encoder's scene cut detection. When a new
    # scene is detected (e.g. a video frame is very different than the one
    # before it), a new keyframe is created. Rarely needs to be adjusted. 0
    # disables scene detection altogether, and uses the GOP size to determine
    # when to create a new keyframe. The recommended default is 40.
    hls_sc_threshold: int = 40
    # Set the Group Picture Size (GOP). Default is 12.
    hls_gop_size: int = 12
    # Set the minimum distance between keyframes.
    hls_keyint_min: int = 25
    # The target length of each segmented file, in seconds. Default is 2.
    hls_target_segment_duration: int = 2
    # The type of HLS playlist to create.
    hls_playlist_type: str = "vod"
    # Enable faster file streaming start for HLS files by moving some of the
    # metadata to the beginning of the file after transcode.
    hls_movflags: str = "+faststart"
    # The encoder profiles to use. Load defaults from the core definitions
    # package.
    hls_encoder_profiles: dict = field(default_factory=dict)

    # The commands we will run to complete this plugin.
    commands: list = field(default_factory=list)
    # Files to output.
    outputs: list = field(default_factory=list)

    def __post_init__(self):
        if self.hls_profile not in self.hls_encoder_profiles:
            self.hls_encoder_profiles = definitions.EncoderProfiles[self.hls_profile]

        if not self.hls_disable:
            # Check to make sure the appropriate binary files we need are installed.
            assert helpers.check_dependencies_binaries(
                required_binaries
            ), AssertionError("Missing required binaries: {}".format(required_binaries))
            print("POSTINIT")

    def cmd(self, job: jobs.StirlingJob):

        if not self.hls_disable:
            if (
                self.video_source_stream == -1
                and job.media_info.preferred["video"] is not None
            ):
                self.video_source_stream = job.media_info.preferred["video"]

            if (
                self.audio_source_stream == -1
                and job.media_info.preferred["audio"] is not None
            ):
                self.audio_source_stream = job.media_info.preferred["audio"]

            if self.hls_audio_sample_rate == 0:
                self.hls_audio_sample_rate = job.media_info.audio_streams[
                    self.audio_source_stream
                ].sample_rate

            output_directory = job.output_directory / self._plugin_name
            output_directory.mkdir(parents=True, exist_ok=True)

            # Set the options to encode an HLS package.
            options = {
                "hide_banner": True,
                "loglevel": "quiet",
                "y": True,
                "i": job.media_info.source,
                "map": "0:v:{} -map 0:a:{}".format(
                    self.video_source_stream, self.audio_source_stream
                ),
                "acodec": self.hls_audio_codec,
                "ar": self.hls_audio_sample_rate,
                "vcodec": self.hls_video_codec,
                "profile:v": self.hls_video_profile,
                "crf": self.hls_crf,
                "sc_threshold": self.hls_sc_threshold,
                "g": self.hls_gop_size,
                "keyint_min": self.hls_keyint_min,
                "hls_time": self.hls_target_segment_duration,
                "hls_playlist_type": self.hls_playlist_type,
                "movflags": self.hls_movflags,
            }

            renditions = ""
            for rendition in self.hls_encoder_profiles:
                rendition_command = {
                    # Scale the video to the appropriate resolution (width and height)
                    "vf": "scale=w={}:h={}:force_original_aspect_ratio=decrease".format(
                        rendition["width"], rendition["height"]
                    ),
                    # Control the bitrate.
                    "b:v": "{}k".format(rendition["bitrate"]),
                    # Set the maximum video bitrate.
                    "maxrate": "{}k".format(
                        int(rendition["bitrate"]) * self.hls_bitrate_ratio
                    ),
                    # Set the size of the buffer before ffmpeg recalculates the
                    # bitrate.
                    "bufsize": "{0}k".format(
                        int(rendition["bitrate"]) * self.hls_buffer_ratio
                    ),
                    # Set the audio output bitrate.
                    "b:a": "{0}k".format(rendition["audio-bitrate"]),
                    # Set the output filename for the HLS segment.
                    "hls_segment_filename": "{0}/{1}_%09d.ts' '{0}/{1}.m3u8".format(
                        str(output_directory), rendition["name"]
                    ),
                }

                renditions += args.default_unparser.unparse(**rendition_command)
                self.outputs.append(
                    "{0}/{1}.m3u8".format(str(output_directory), rendition["name"])
                )

            self.commands.append(
                "ffmpeg {} {}".format(
                    args.default_unparser.unparse(
                        str(job.media_info.source), **options
                    ),
                    renditions,
                )
            )
            self.outputs.append(output_directory)


@dataclass
class StirlingCmdHLS(definitions.StirlingCmd):
    """StirlingCmdHLS contains a mapping of our input arguments to the necessary
    CLI arguments that our video transcoder will need. Currently, we use ffmpeg,
    but others could be used by mapping the proper input parameters to the
    command parameters our transcoder requires."""

    # The default, common CLI settings to use
    cli_options: dict = field(default_factory=dict)

    # A set of input options for the encoder.
    input_options: dict = field(default_factory=dict)

    options: dict = field(default_factory=dict)

    def options(self, args: StirlingPluginHLS):
        """options returns a list of options to pass to the transcoder."""
        self.options = collections.OrderedDict(
            {
                # Audio codec to encode with.
                "acodec": args.hls_audio_codec,
                # Audio sample rate to encode with.
                "ar": args.hls_audio_sample_rate,
                # Video codec to encode with.
                "vcodec": args.hls_video_codec,
                # Video encoding profile.
                "profile:v": args.hls_video_profile,
                "crf": args.hls_crf,
                # Scenecut detection threshold.
                "sc_threshold": args.hls_sc_threshold,
                # Set the Group Picture Size (GOP).
                "g": args.hls_gop_size,
                # Set the minimum distance between keyframes.
                "keyint_min": args.hls_keyint_min,
                # The target length of each segmented file.
                "hls_time": args.hls_target_segment_duration,
                # The type of HLS playlist to create.
                "hls_playlist_type": args.hls_playlist_type,
                # Enable faster file streaming start for HLS files by moving
                # some of the metadata to the beginning of the file after
                # transcode.
                "movflags": args.hls_movflags,
            }
        )
        self.rendition_options = (
            collections.OrderedDict(
                {
                    # Scale the video to the appropriate resolution (width and height)
                    "vf": "scale=w={}:h={}:force_original_aspect_ratio=decrease",
                    # Control the bitrate.
                    "b:v": "{}k",
                    # Set the maximum video bitrate.
                    "maxrate": "{0}k",
                    # Set the size of the buffer before ffmpeg recalculates the
                    # bitrate.
                    "bufsize": "{0}k",
                    # Set the audio output bitrate.
                    "b:a": "{0}k",
                    # Set the output filename for the HLS segment.
                    "hls_segment_filename": "{0}/{1}_%09d.ts' '{0}/{1}.m3u8",
                }
            ),
        )


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
        this_rendition["c"] = this_rendition["hls_segment_filename"].format(
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

        # Video encoding options Set the output folder for the HLS segments and
        # playlists. Currently this is the same as the full package output
        # folder, but we're making it a variable here in case we want to change
        # it later. Update our templates with calculated values Calculate the
        # appropriate interval for inserting keyframes.
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

        # Set the maximum distance between keyframes. Currently, we"re setting
        # this the same as kf_interval.
        job["commands"]["hls"]["options"]["g"] = str(
            kf_interval * job["arguments"]["hls_keyframe_multiplier"]
        )

        # Set the Constant Rate Factor to normalize the bitrate throughout for
        # easier streaming.
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

        # Create template entries for each of the encoder renditions specified
        # in the profile.
        job, renditions_options, encoder_renditions, output_playlist = create_rendition(
            job
        )

        for rendition_option in renditions_options:
            encoder_renditions += " " + args.default_unparser.unparse(
                **(job["commands"]["hls"]["options"] | rendition_option)
            )

        # Fix unargparsers insistence on "deciding" which types of quotes to
        # use.
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
