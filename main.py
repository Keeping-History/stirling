import core.job as job
from plugins import audio, video, frames, hls, peaks, transcript

# TODO: Add support for multiple audio tracks.
# TODO: Add support for multiple transcripts/languages
# TODO: We need to create a separate ffmpeg call with the lowest quality settings
# at the source files resolution for previewing and fast editor preview.

if __name__ == "__main__":

    # Create a new job
    my_job = job.StirlingJob(source="source.mp4", debug=True)

    # Add plugins to the job
    my_job.add_plugins(
        video.StirlingPluginVideo(),
        audio.StirlingPluginAudio(),
        peaks.StirlingPluginPeaks(),
        frames.StirlingPluginFrames(),
        transcript.StirlingPluginTranscript(),
        hls.StirlingPluginHLS(),
    )

    # Run the job
    my_job.run()

    # Close out the job
    my_job.close()
