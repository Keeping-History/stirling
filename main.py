from core import audio, jobs, video
from plugins import hls, peaks, transcript

# TODO: Add support for multiple audio tracks.
# TODO: Add support for multiple transcripts/languages
# TODO: Revisit https://github.com/kkroening/ffmpeg-python/tree/master/ffmpeg for argument creation
# TODO: We need to create a separate ffmpeg call with the lowest quality settings
# at the source files resolution for previewing and fast editor preview.

if __name__ == "__main__":

    # Create a new job
    my_job = jobs.StirlingJob(source="source.mp4", debug=True)

    # Add plugins to the job
    my_job.add_plugins(
        audio.StirlingPluginAudio(),
        peaks.StirlingPluginPeaks(),
        video.StirlingPluginVideo(),
        transcript.StirlingPluginTranscript(),
        hls.StirlingPluginHLS(),
    )

    # Run the job
    my_job.run()

    # Close out the job
    my_job.close()
