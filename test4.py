# # print(hints["log_file"])
# f.time_start= "2020-01-01"
# f.time_end = datetime.now()

# f.job_file = "/path/job.json_file"
# f.duration = "1.09"

# print(json.dumps(f, cls=helpers.StirlingJSONEncoder, indent=4))
# sleep(100)


## VALID OUTPUT FROM OLD JOB GENERATOR
# {
#   "id": "7cad3a70-387a-44c9-a1c6-ee38197ca542",
#   "time_start": "2022-10-13 15:13:52.006377",
#   "time_end": null,
#   "duration": null,
#   "log_file": null,
#   "job_file": null,
#   "arguments": {
#     "source": null,
#     "output": null,
#     "input_directory": null,
#     "output_directory_prefix": "output",
#     "source_delete_disable": true,
#     "source_copy_disable": true,
#     "audio_disable": false,
#     "transcript_disable": false,
#     "peaks_disable": false,
#     "hls_disable": false,
#     "video_frames_disable": false,
#     "hls_profile": "sd",
#     "input_video_stream": -1,
#     "input_audio_stream": -1,
#     "hls_segment_duration": 4,
#     "hls_bitrate_ratio": 1.07,
#     "hls_buffer_ratio": 1.5,
#     "hls_crf": 20,
#     "hls_keyframe_multiplier": 1,
#     "frames_interval": 1,
#     "simulate": false,
#     "debug": true,
#     "job_file": null
#   },
#   "output": { "directory": null, "outputs": [] },
#   "commands": {
#     "hls": {
#       "command": null,
#       "output": null,
#       "args": {
#         "hls_profile": "sd",
#         "hls_bitrate_ratio": 1,
#         "hls_buffer_ratio": 1
#       },
#       "input_options": { "i": null, "map": null },
#       "output_options": { "directory": null },
#       "cli_options": { "hide_banner": true, "y": true, "loglevel": "debug" },
#       "options": {
#         "acodec": "aac",
#         "ar": "44100",
#         "vcodec": "h264",
#         "profile:v": "main",
#         "crf": "20",
#         "sc_threshold": "40",
#         "g": "12",
#         "keyint_min": "25",
#         "hls_time": "2",
#         "hls_playlist_type": "vod",
#         "movflags": "+faststart",
#         "vf": "",
#         "b:v": "",
#         "maxrate": "",
#         "bufsize": "",
#         "b:a": ""
#       },
#       "rendition_options": {
#         "vf": "scale=w={}:h={}:force_original_aspect_ratio=decrease",
#         "b:v": "{}k",
#         "maxrate": "{0}k",
#         "bufsize": "{0}k",
#         "b:a": "{0}k",
#         "hls_segment_filename": "{0}/{1}_%09d.ts' '{0}/{1}.m3u8"
#       },
#       "encoder_profiles": {
#         "sd": [
#           {
#             "name": "120p",
#             "width": "160",
#             "height": "120",
#             "bitrate": "128",
#             "audio-bitrate": "32",
#             "ratio": "4:3"
#           },
#           {
#             "name": "240p",
#             "width": "320",
#             "height": "240",
#             "bitrate": "300",
#             "audio-bitrate": "64",
#             "ratio": "4:3"
#           },
#           {
#             "name": "480p",
#             "width": "640",
#             "height": "480",
#             "bitrate": "800",
#             "audio-bitrate": "96",
#             "ratio": "4:3"
#           }
#         ],
#         "hd": [
#           {
#             "name": "720p",
#             "width": "1280",
#             "height": "720",
#             "bitrate": "7400",
#             "audio-bitrate": "128",
#             "ratio": "16:9"
#           },
#           {
#             "name": "1080p",
#             "width": "1920",
#             "height": "1080",
#             "bitrate": "7400",
#             "audio-bitrate": "128",
#             "ratio": "16:9"
#           },
#           {
#             "name": "1080p-high",
#             "width": "1920",
#             "height": "1080",
#             "bitrate": "7400",
#             "audio-bitrate": "192",
#             "ratio": "16:9"
#           }
#         ]
#       }
#     },
#     "transcript": {
#       "command": null,
#       "output": null,
#       "options": { "o": null, "D": "en", "S": "en", "C": "10", "F": "json" }
#     },
#     "peaks": {
#       "command": null,
#       "output": null,
#       "options": { "i": null, "o": null }
#     },
#     "audio": {
#       "command": null,
#       "output": null,
#       "cli_options": { "hide_banner": true, "y": true, "loglevel": "debug" },
#       "options": { "i": "", "ac": "1", "acodec": "pcm_s16le", "ar": "44800" }
#     },
#     "frames": {
#       "command": null,
#       "output": null,
#       "args": { "fps": 1, "output_filename": "%d.jpg" },
#       "cli_options": { "hide_banner": true, "y": true, "loglevel": "debug" },
#       "options": { "i": "", "r": "{}", "vsync": 0 }
#     }
#   },
#   "source": {
#     "info": {},
#     "input": { "filename": null, "video_stream": null, "audio_stream": null }
#   }
# }
