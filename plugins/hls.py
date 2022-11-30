from dataclasses import dataclass, field

from core import core, job

required_binaries = ["ffmpeg"]


@dataclass
class StirlingPluginHLS(core.StirlingPlugin):
    """StirlingPluginHLS is for creating an HLS VOD streaming package from
    the input source video."""

    name: str = "hls"
    depends_on: list = field(default_factory=lambda: ["video"])
    priority: int = 50

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
    # The encoder profiles to use. Load defaults from the core core
    # package.
    hls_encoder_profiles: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.hls_profile not in self.hls_encoder_profiles:
            self.hls_encoder_profiles = core.VideoEncoderProfiles[self.hls_profile]

        if not self.hls_disable:
            # Check to make sure the appropriate binary files we need are installed.
            assert core.check_dependencies_binaries(required_binaries), AssertionError(
                "Missing required binaries: {}".format(required_binaries)
            )

    def cmd(self, this_job: job.StirlingJob):
        if not self.hls_disable:
            preferred_audio_stream = this_job.media_info.get_preferred_stream("audio")
            preferred_video_stream = this_job.media_info.get_preferred_stream("video")

            if self.video_source_stream == -1:
                self.video_source_stream = preferred_video_stream.stream

            if self.audio_source_stream == -1:
                self.audio_source_stream = preferred_audio_stream.stream

            if self.hls_audio_sample_rate == 0:
                self.hls_audio_sample_rate = preferred_audio_stream.sample_rate

            output_directory = this_job.output_directory / self.name
            output_directory.mkdir(parents=True, exist_ok=True)

            outputs = []

            # Set the options to encode an HLS package.
            options = {
                "hide_banner": True,
                "y": True,
                "i": this_job.media_info.source,
            }

            video_options = {
                "map": "0:v:{}".format(self.video_source_stream),
                "vcodec": self.hls_video_codec,
                "profile:v": self.hls_video_profile,
                "crf": self.hls_crf,
                "hls_time": self.hls_target_segment_duration,
                "hls_playlist_type": self.hls_playlist_type,
                "sc_threshold": self.hls_sc_threshold,
                "g": self.hls_gop_size,
                "keyint_min": self.hls_keyint_min,
                "movflags": self.hls_movflags,
            }

            audio_options = {
                "map": "0:a:{}".format(
                    self.audio_source_stream - len(this_job.media_info.video_streams)
                ),
                "acodec": self.hls_audio_codec,
                "ar": self.hls_audio_sample_rate,
            }

            renditions = ""
            master_playlist_contents = "#EXTM3U\n#EXT-X-VERSION:3\n"
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
                    # Ensure the m3u8 contains the entire stream, as ffmpeg
                    # will default and limit this to only 5 entries.
                    "hls_list_size": 0,
                    # Set the output filename for the HLS segment.
                    "hls_segment_filename": "'{0}/{1}_%09d.ts'".format(
                        str(output_directory), rendition["name"]
                    ),
                }
                master_playlist_contents += (
                    "#EXT-X-STREAM-INF:BANDWIDTH={},RESOLUTION={}x{}\n{}.m3u8\n".format(
                        int(rendition["bitrate"]) * 1000,
                        rendition["width"],
                        rendition["height"],
                        rendition["name"],
                    )
                )

                rendition_playlist = "{0}/{1}.m3u8".format(
                    str(output_directory), rendition["name"]
                )
                outputs.append(output_directory / rendition_playlist)

                renditions += (
                    core.ffmpeg_unparser.unparse(**rendition_command)
                    + " "
                    + rendition_playlist
                    + " "
                )

            master_playlist = "playlist.m3u8"
            outputs.append(output_directory / master_playlist)

            this_job.commands.append(
                core.StirlingCmd(
                    name=self.name + "_master_playlist",
                    command="echo '{}' > {}".format(
                        master_playlist_contents,
                        str(output_directory / master_playlist),
                    ),
                    priority=self.priority,
                    expected_output=str(output_directory / master_playlist),
                    depends_on=self.depends_on,
                )
            )

            this_job.commands.append(
                core.StirlingCmd(
                    name=self.name,
                    command="ffmpeg {} {} {} {}".format(
                        core.ffmpeg_unparser.unparse(**options),
                        core.ffmpeg_unparser.unparse(**video_options),
                        core.ffmpeg_unparser.unparse(**audio_options),
                        renditions,
                    ),
                    priority=self.priority,
                    expected_output=str(output_directory),
                    depends_on=self.depends_on,
                )
            )


# ## PLUGIN FUNCTIONS
# ## Generate an HLS Package from file
# def create_rendition(this_job):
#     # Set some holding variables
#     renditions_options, encoder_renditions = [], ""

#     # Set some variables for easier reading
#     encoding_profile = this_job["commands"]["hls"]["core"]["hls_profile"]

#     this_job["commands"]["hls"]["output_options"]["directory"] = pathlib.Path(
#         this_job["commands"]["hls"]["output_options"]["directory"]
#     )

#     # Holder for the master m3u8 file contents.
#     output_playlist = "#EXTM3U\n#EXT-X-VERSION:3\n"
#     core.log(this_job, "Creating renditions.")
#     core.log(
#         this_job,
#         "Profile in use is '{}'.".format(encoding_profile),
#     )

#     for rendition in this_job["commands"]["hls"]["encoder_profiles"][encoding_profile]:
#         core.log(
#             this_job,
#             "Creating rendition options for file  {}, rendition {}.".format(
#                 str(this_job["commands"]["hls"]["output_options"]["directory"]),
#                 str(rendition["name"]),
#             ),
#         )

#         output_playlist += (
#             "#EXT-X-STREAM-INF:BANDWIDTH={},RESOLUTION={}x{}\n{}.m3u8\n".format(
#                 int(rendition["bitrate"]) * 1000,
#                 rendition["width"],
#                 rendition["height"],
#                 rendition["name"],
#             )
#         )

#         this_rendition = this_job["commands"]["hls"]["rendition_options"].copy()
#         this_rendition["vf"] = this_rendition["vf"].format(
#             rendition["width"], rendition["height"]
#         )
#         this_rendition["b:v"] = this_rendition["b:v"].format(rendition["bitrate"])
#         this_rendition["b:a"] = this_rendition["b:a"].format(rendition["audio-bitrate"])
#         this_rendition["maxrate"] = this_rendition["maxrate"].format(
#             int(
#                 float(rendition["bitrate"])
#                 * this_job["commands"]["hls"]["core"]["hls_bitrate_ratio"]
#             )
#         )
#         this_rendition["bufsize"] = this_rendition["bufsize"].format(
#             int(
#                 float(rendition["bitrate"])
#                 * this_job["commands"]["hls"]["core"]["hls_buffer_ratio"]
#             )
#         )
#         this_rendition["c"] = this_rendition["hls_segment_filename"].format(
#             str(this_job["commands"]["hls"]["output_options"]["directory"]),
#             rendition["name"],
#         )
#         renditions_options.append(this_rendition)

#     return this_job, renditions_options, encoder_renditions, output_playlist


# def create_hls(this_job):
#     if not this_job["arguments"]["hls_disable"]:
#         # Check to make sure the appropriate binary files we need are installed.
#         assert core.check_dependencies_binaries(required_binaries), core.log(
#             core.check_dependencies_binaries(required_binaries)
#         )

#         # Create the directory for the hls package.
#         hls_output_directory = this_job["output"]["directory"] / "video" / "hls"
#         hls_output_directory.mkdir(parents=True, exist_ok=True)

#         # Video encoding options Set the output folder for the HLS segments and
#         # playlists. Currently this is the same as the full package output
#         # folder, but we're making it a variable here in case we want to change
#         # it later. Update our templates with calculated values Calculate the
#         # appropriate interval for inserting keyframes.
#         try:
#             kf_interval = (
#                 eval(
#                     this_job["source"]["info"]["streams"][
#                         this_job["source"]["input"]["video_stream"]
#                     ]["avg_frame_rate"]
#                 )
#                 * 2
#             )
#         except (ValueError, TypeError):
#             kf_interval = 60

#         # Where to save the HLS output package files.
#         this_job["commands"]["hls"]["output_options"]["directory"] = str(
#             hls_output_directory
#         )

#         # Set the minimum distance between keyframes.
#         this_job["commands"]["hls"]["options"]["keyint_min"] = str(kf_interval)

#         # Set the maximum distance between keyframes. Currently, we"re setting
#         # this the same as kf_interval.
#         this_job["commands"]["hls"]["options"]["g"] = str(
#             kf_interval * this_job["arguments"]["hls_keyframe_multiplier"]
#         )

#         # Set the Constant Rate Factor to normalize the bitrate throughout for
#         # easier streaming.
#         this_job["commands"]["hls"]["options"]["crf"] = str(this_job["arguments"]["hls_crf"])

#         # Set the length of each h.264 TS segment file.
#         this_job["commands"]["hls"]["options"]["hls_time"] == str(
#             this_job["arguments"]["hls_segment_duration"]
#         )

#         # The main input file
#         this_job["commands"]["hls"]["input_options"]["i"] = this_job["source"]["input"][
#             "filename"
#         ]
#         this_job["commands"]["hls"]["input_options"]["map"] = "0:{}".format(
#             str(this_job["source"]["input"]["video_stream"])
#         )

#         # The HLS profile to use. See encoder_profiles for more information.
#         this_job["commands"]["hls"]["core"]["hls_profile"] == str(
#             this_job["arguments"]["hls_profile"]
#         )

#         # These two values help us fine-tune the HLS encoding.
#         this_job["commands"]["hls"]["core"]["hls_bitrate_ratio"] == str(
#             this_job["arguments"]["hls_bitrate_ratio"]
#         )
#         this_job["commands"]["hls"]["core"]["hls_buffer_ratio"] == str(
#             this_job["arguments"]["hls_buffer_ratio"]
#         )

#         # Create template entries for each of the encoder renditions specified
#         # in the profile.
#         this_job, renditions_options, encoder_renditions, output_playlist = create_rendition(
#             this_job
#         )

#         for rendition_option in renditions_options:
#             encoder_renditions += " " + core.default_unparser.unparse(
#                 **(this_job["commands"]["hls"]["options"] | rendition_option)
#             )

#         # Fix unargparsers insistence on "deciding" which types of quotes to
#         # use.
#         encoder_renditions = encoder_renditions.replace("'", '"')

#         this_job["commands"]["hls"]["command"] = "ffmpeg " + (
#             core.ffmpeg_unparser.unparse(
#                 **(
#                     this_job["commands"]["hls"]["cli_options"]
#                     | this_job["commands"]["hls"]["input_options"]
#                 )
#             )
#             + " "
#             + encoder_renditions
#         )

#         core.log(this_job, "HLS Encoding Command: " + this_job["commands"]["hls"]["command"])

#         # Convert the video file to packaged HLS.
#         core.log(
#             this_job,
#             "Generating HLS package from source file '{}' to directory '{}'".format(
#                 this_job["commands"]["hls"]["input_options"]["i"],
#                 str(this_job["commands"]["hls"]["output_options"]["directory"]),
#             ),
#         )

#         # Create an m3u8 file to hold all the renditions.
#         this_job = create_master_playlist(this_job, output_playlist)

#         this_job["output"]["video_hls_generation"] = plugins.do(
#             this_job["commands"]["hls"]["command"], this_job["arguments"]["simulate"]
#         )
#         core.log(
#             this_job,
#             "Created HLS video package in {0}".format(
#                 str(this_job["commands"]["hls"]["output_options"]["directory"])
#             ),
#         )

#         this_job["output"]["outputs"].append(
#             this_job["commands"]["hls"]["output_options"]["directory"]
#         )

#     return this_job


# def create_master_playlist(this_job, output_playlist):
#     playlist = str(
#         this_job["commands"]["hls"]["output_options"]["directory"] / "playlist.m3u8"
#     )
#     # Create an m3u8 file to hold all the renditions.
#     core.log(
#         this_job,
#         "Creating m3u8 playlist file {0}".format(playlist),
#     )
#     if not this_job["arguments"]["simulate"]:
#         m3u8_file = open(
#             playlist,
#             "w",
#         )
#         m3u8_file.write(output_playlist)
#         m3u8_file.close()

#         core.log(
#             this_job,
#             "Created m3u8 playlist file {0}".format(playlist),
#         )

#         this_job["output"]["outputs"].append(
#             this_job["commands"]["hls"]["output_options"]["directory"] / "playlist.m3u8"
#         )

#     return this_job
