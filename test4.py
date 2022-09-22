import json
from core import definitions, strings
from typing import get_type_hints

from datetime import datetime

# e = definitions.Job()
# e.duration = 100
# e.log_file = "job.log"
# e.job_file = "job.json"
# print(json.dumps(e, cls=strings.JobEncoder))

f = definitions.Job(id="e491aca4-d0e1-4db0-826f-df949809f848")
print(f.id, type(f.id))
# # if isinstance(f, (int, type(None))):
# #     print("yep")

# coreargs = definitions.ArgumentsCore()
# jobargs = definitions.ArgumentsJob()
# framesargs = definitions.ArgumentsPluginFrames()
# transcriptargs = definitions.ArgumentsPluginTranscript()
# peakargs = definitions.ArgumentsPluginPeaks()
# hlsargs = definitions.ArgumentsPluginHLS()

# f.arguments = {**coreargs.__dict__, **jobargs.__dict__, **framesargs.__dict__, **transcriptargs.__dict__, **peakargs.__dict__, **hlsargs.__dict__}
# print(json.dumps(f, cls=strings.JobEncoder, indent=4))

# hints = get_type_hints(definitions.Job)

# print(hints["log_file"])
f.time_end = datetime.now()

f.time_start = "2022-01-02"
f.job_file = "/path/job.json_file"
f.duration = 1

print(type(f.time_end))
print(f.time_end)
print(f.time_start)
print(f.job_file)
