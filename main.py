import shutil
from pathlib import Path

from stirling.job import StirlingJob

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

    print(my_job.framework.trim(1, 2, my_job.media_info.get_preferred_stream("audio")))

    # codecs = [
    #     StirlingFFMpegMediaCodecAudioMP3(framework=my_job.framework),
    #     StirlingFFMpegMediaCodecAudioPCM(framework=my_job.framework),
    # ]
    #
    # containers = [
    #     StirlingMediaContainerAudioMP3(),
    #     StirlingMediaContainerAudioWAV(),
    # ]
    #
    # audio_plugin = StirlingPluginAudio(
    #     options={
    #         "source": input_file,
    #         "source_stream": 0,
    #         "codec": codecs[0],
    #         "container": containers[0],
    #     }
    # )
    #
    #
    # print(audio_plugin.cmds(my_job))
    #
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
