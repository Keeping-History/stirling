import shutil
from pathlib import Path

from stirling.containers.audio.mp3 import StirlingMediaContainerAudioMP3
from stirling.containers.audio.wav import StirlingMediaContainerAudioWAV
from stirling.frameworks.ffmpeg.codecs.mp3 import StirlingFFMpegMediaCodecAudioMP3
from stirling.frameworks.ffmpeg.codecs.pcm import StirlingFFMpegMediaCodecAudioPCM
from stirling.job import StirlingJob
from stirling.plugins.audio.core import StirlingPluginAudio

if __name__ == "__main__":
    # Remove the output directory every time, for testing.
    output_path = Path("./output")
    if output_path.is_dir():
        shutil.rmtree(output_path)

    # Create a new job.json from a file.
    input_file = Path("./examples/source.mp4")
    my_job = StirlingJob(
        source=input_file,
    )
    print(my_job.framework.codec())
    exit()

    codecs = [
        StirlingFFMpegMediaCodecAudioMP3(framework=my_job.framework),
        StirlingFFMpegMediaCodecAudioPCM(framework=my_job.framework),
    ]

    containers = [
        StirlingMediaContainerAudioMP3(),
        StirlingMediaContainerAudioWAV(),
    ]

    audio_plugin = StirlingPluginAudio()
    #
    # print(audio_plugin.cmds(my_job))
    #
    # # Add plugins to the job.json
    my_job.add_plugins(audio_plugin)
    audio_plugin2 = my_job.plugins[0]
    audio_plugin2.command("trim", {"time_start": 0, "time_end": 10})
    audio_plugin2.cmds(my_job)

    #     video.StirlingPluginVideo(),
    #     audio.StirlingPluginAudio(),
    #     peaks.StirlingPluginPeaks(),
    #     frames.StirlingPluginFrames(),
    #     transcript.StirlingPluginTranscript(),
    #     hls.StirlingPluginHLS(),
    # )

    # # Run the job.json
    # my_job.run()

    # # Close out the job.json
    my_job.close()
    # a = av1.StirlingVideoEncoderAV1()

    # a = json.dumps(my_job, cls=StirlingJSONEncoder, indent=4)
    # print(a)
