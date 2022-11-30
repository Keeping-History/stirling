# import json
# import os

# import cv2
# from mtcnn import MTCNN

# from core import core

# # from core import pytorch
# from plugins import plugins


# ## PLUGIN FUNCTIONS
# ## Generate an HLS Package from file
# def generate_face_detection(job):
#     if not job["arguments"]["disable_object_detection"]:
#         # Create the directory for the faces.
#         frames_input_directory = job["output"]["directory"] / "img" / "frames"

#         # device = pytorch.pytorch_get_device()

#         detector = MTCNN()
#         output_filename = str(job["output"]["directory"]) + "/annotations/faces.json"

#         output_file = open(output_filename, "w")
#         scan: list[dict] = []

#         # iterate over files in
#         # that directory
#         for filename in os.listdir(frames_input_directory):
#             if filename.endswith((".jpg", ".png")):
#                 #f = os.path.join(directory, filename)
#                 f = ""
#                 holder: dict = {"filename": filename, "faces": []}
#                 if os.path.isfile(f):
#                     img = cv2.cvtColor(cv2.imread(f), cv2.COLOR_BGRA2BGR)
#                     faces = detector.detect_faces(img)
#                     holder["faces"] = faces
#                     for i, face in enumerate(holder["faces"]):
#                         cropped_face = img[
#                             face["box"][1] : face["box"][1] + face["box"][3],
#                             face["box"][0] : face["box"][0] + face["box"][2],
#                         ]
#                         cv2.imwrite(f + "_" + str(i) + "_face.jpg", cropped_face)
#                     scan.append(holder)

#         output_file.writelines(json.dumps(scan) + "\n")
#         output_file.close()

#         # Create the directory for the hls package.
#         hls_output_directory = job["output"]["directory"] / "video" / "hls"
#         hls_output_directory.mkdir(parents=True, exist_ok=True)

#         # Video encoding options
#         # Set the output folder for the HLS segments and playlists. Currently
#         # this is the same as the full package output folder, but we're making it a
#         # variable here in case we want to change it later.
#         # Update our templates with calculated values
#         # Calculate the appropriate interval for inserting keyframes.
#         try:
#             kf_interval = (
#                 eval(
#                     job["source"]["info"]["streams"][
#                         job["source"]["input"]["video_stream"]
#                     ]["avg_frame_rate"]
#                 )
#                 * 2
#             )
#         except (ValueError, TypeError):
#             kf_interval = 60

#         # Where to save the HLS output package files.
#         job["commands"]["hls"]["output_options"]["directory"] = str(
#             hls_output_directory
#         )

#         # Set the minimum distance between keyframes.
#         job["commands"]["hls"]["options"]["keyint_min"] = str(kf_interval)

#         # Set the maximum distance between keyframes. Currently, we"re setting this the same as kf_interval.
#         job["commands"]["hls"]["options"]["g"] = str(
#             kf_interval * job["arguments"]["hls_keyframe_multiplier"]
#         )

#         # Set the Constant Rate Factor to normalize the bitrate throughout for easier streaming.
#         job["commands"]["hls"]["options"]["crf"] = str(job["arguments"]["hls_crf"])

#         # Set the length of each h.264 TS segment file.
#         job["commands"]["hls"]["options"]["hls_time"] == str(
#             job["arguments"]["hls_segment_duration"]
#         )

#         # The main input file
#         job["commands"]["hls"]["input_options"]["i"] = job["source"]["input"][
#             "filename"
#         ]
#         job["commands"]["hls"]["input_options"]["map"] = "0:{}".format(
#             str(job["source"]["input"]["video_stream"])
#         )

#         # The HLS profile to use. See encoder_profiles for more information.
#         job["commands"]["hls"]["args"]["hls_profile"] == str(
#             job["arguments"]["hls_profile"]
#         )

#         # These two values help us fine-tune the HLS encoding.
#         job["commands"]["hls"]["args"]["hls_bitrate_ratio"] == str(
#             job["arguments"]["hls_bitrate_ratio"]
#         )
#         job["commands"]["hls"]["args"]["hls_buffer_ratio"] == str(
#             job["arguments"]["hls_buffer_ratio"]
#         )

#         # Create template entries for each of the encoder renditions specified in the profile.
#         job, renditions_options, encoder_renditions, output_playlist = create_rendition(
#             job
#         )

#         for rendition_option in renditions_options:
#             encoder_renditions += " " + core.default_unparser.unparse(
#                 **(job["commands"]["hls"]["options"] | rendition_option)
#             )

#         # Fix unargparsers insistence on "deciding" which types of quotes to use.
#         encoder_renditions = encoder_renditions.replace("'", '"')

#         job["commands"]["hls"]["command"] = "ffmpeg " + (
#             core.ffmpeg_unparser.unparse(
#                 **(
#                     job["commands"]["hls"]["cli_options"]
#                     | job["commands"]["hls"]["input_options"]
#                 )
#             )
#             + " "
#             + encoder_renditions
#         )

#         core.log(job, "HLS Encoding Command: " + job["commands"]["hls"]["command"])

#         # Convert the video file to packaged HLS.
#         core.log(
#             job,
#             "Generating HLS package from source file '{}' to directory '{}'".format(
#                 job["commands"]["hls"]["input_options"]["i"],
#                 str(job["commands"]["hls"]["output_options"]["directory"]),
#             ),
#         )

#         # Create an m3u8 file to hold all the renditions.
#         job = create_master_playlist(job, output_playlist)

#         job["output"]["video_hls_generation"] = plugins.do(
#             job["commands"]["hls"]["command"], job["arguments"]["simulate"]
#         )
#         core.log(
#             job,
#             "Created HLS video package in {0}".format(
#                 str(job["commands"]["hls"]["output_options"]["directory"])
#             ),
#         )

#         job["output"]["outputs"].append(
#             job["commands"]["hls"]["output_options"]["directory"]
#         )

#     return job
