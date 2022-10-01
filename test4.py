import json

from core import definitions, strings, video, jobs
from plugins import hls, peaks, transcript

# e = definitions.Job()
# e.duration = 100
# e.log_file = "job.log"
# e.job_file = "job.json"
# print(json.dumps(e, cls=strings.JobEncoder))

#f = definitions.StirlingJob(id="e491aca4-d0e1-4db0-826f-df949809f848")
f = jobs.create_job()
# # if isinstance(f, (int, type(None))):
# #     print("yep")
j = jobs.create_job_from_template()

coreargs = definitions.StirlingArgsCore()
jobargs = definitions.StirlingArgsJob()
framesargs = video.StirlingArgsPluginFrames()
transcriptargs = transcript.StirlingArgsPluginTranscript()
peakargs = peaks.StirlingArgsPluginPeaks()
hlsargs = hls.StirlingArgsPluginHLS()
outputs = definitions.StirlingOutputs(
    directory=".", outputs=[{"plugin": "a", "files": "a"}]
)
f.output = outputs

f.arguments = {
    framesargs.__class__.__name__: framesargs.__dict__,
    transcriptargs.__class__.__name__: transcriptargs.__dict__,
    peakargs.__class__.__name__: peakargs.__dict__,
    hlsargs.__class__.__name__:hlsargs.__dict__,
    }

print(json.dumps(f, cls=strings.JobEncoder, indent=4))
#print(json.dumps(j, cls=strings.JobEncoder, indent=4))
exit()

# # print(hints["log_file"])
# f.time_start= "2020-01-01"
# f.time_end = datetime.now()

# f.job_file = "/path/job.json_file"
# f.duration = "1.09"

# print(json.dumps(f, cls=strings.JobEncoder, indent=4))
# sleep(100)
