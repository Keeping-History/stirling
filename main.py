import json
import shutil
from pathlib import Path

from stirling.encodings import StirlingJSONEncoder
from stirling.frameworks.ffmpeg import StirlingMediaFrameworkFFMpeg
from stirling.job import StirlingJob

if __name__ == "__main__":
    # Remove the output directory every time, for testing.
    output_path = Path("./output")
    if output_path.exists() and output_path.is_dir():
        shutil.rmtree(output_path)

    # Create a new job from a file.
    input_file = Path("./examples/source.mp4")
    my_job = StirlingJob(source=input_file, framework=StirlingMediaFrameworkFFMpeg())

    # # Add plugins to the job
    # my_job.add_plugins(
    #     video.StirlingPluginVideo(),
    #     audio.StirlingPluginAudio(),
    #     peaks.StirlingPluginPeaks(),
    #     frames.StirlingPluginFrames(),
    #     transcript.StirlingPluginTranscript(),
    #     hls.StirlingPluginHLS(),
    # )

    # # Run the job
    # my_job.run()

    # # Close out the job
    # my_job.close()
    # a = av1.StirlingVideoEncoderAV1()

    a = json.dumps(my_job, cls=StirlingJSONEncoder, indent=4)
    print(a)
