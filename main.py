import sys

from core import audio, jobs, probe, video
from plugins import plugins

# TODO: Add support for multiple audio tracks.
# TODO: Add support for multiple transcripts/languages
# TODO: Revisit https://github.com/kkroening/ffmpeg-python/tree/master/ffmpeg for argument creation
# TODO: We need to create a separate ffmpeg call with the lowest quality settings
# at the source files resolution for previewing and fast editor preview.

if __name__ == "__main__":
    # BEGIN

    # Create our job dictionary that will store all the information
    # about the job and ceate a timestamp of when we started this job,
    # and create a unique UUID to identify this job, the output file,
    # and the output directory (when not specified explicitly).
    job = jobs.create_job_from_template()

    # Open the job and pass the command-line arguments to the job.
    job = jobs.open_job(job, sys.argv[1:])

    # CORE FUNCTIONS
    # Media Probe
    job = probe.probe(job)

    # Audio Extraction
    job = audio.extract_audio(job)

    # Image Frame Extraction
    job = video.extract_frames(job)

    # Run the plugins
    job = plugins.run(job)

    # END
    jobs.close_job(job)
