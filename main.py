import shutil
from pathlib import Path

from stirling.frameworks.ffmpeg.codecs.mp3 import (
    StirlingFFMpegMediaCodecAudioMP3,
)
from stirling.frameworks.ffmpeg.codecs.pcm import (
    StirlingFFMpegMediaCodecAudioPCM,
)
from stirling.frameworks.ffmpeg.core import StirlingMediaFrameworkFFMpeg
from stirling.job import StirlingJob, StirlingJobOptions
from stirling.logger import StirlingLoggerLevel

if __name__ == "__main__":
    # Remove the output directory every time, for testing.
    output_path = Path("./output")
    if output_path.is_dir():
        shutil.rmtree(output_path)

    # Create a new job from a file.
    input_file = Path("./examples/source.mp4")
    my_job = StirlingJob(
        source=input_file,
    )

    # codecs = [
    #     StirlingFFMpegMediaCodecAudioMP3(stream=1),
    #     StirlingFFMpegMediaCodecAudioPCM(stream=2),
    # ]
    #
    # print([codec.get() for codec in codecs])

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
    my_job.close()
    # a = av1.StirlingVideoEncoderAV1()

    # a = json.dumps(my_job, cls=StirlingJSONEncoder, indent=4)
    # print(a)
