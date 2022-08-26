import subprocess

from plugins import hls, peaks, transcript


def run(job):

    # PLUGIN FUNCTIONS
    # Generate Audio Peaks
    job = peaks.generate_peaks(job)

    # Generate Transcripts
    job = transcript.generate_transcript(job)

    # Generate an HLS VOD package
    job = hls.create_hls(job)

    return job


def do(command, simulate=False):
    cmd_output = [""]
    if not simulate:
        cmd_output = subprocess.getstatusoutput(command)

    return cmd_output[1]
