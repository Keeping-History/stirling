from mtcnn import MTCNN
import torch
import json
import cv2
import os
import numpy as np
from pathlib import Path

# assign directory
directory = Path('/Users/robbiebyrd/Projects/stirling/output/6014cc1e-72b0-41b5-b351-e77e2e9c9f4b/img/frames')
device = torch.device("mps")
print('Running on device: {}'.format(device))
detector = MTCNN()

output_file = open(directory / "faces.json", "w")
scan: list[dict] = []

# iterate over files in
# that directory
for filename in os.listdir(directory):
    if filename.endswith(('.jpg', '.png')):
        f = os.path.join(directory, filename)
        holder: dict = {
            "filename": filename,
            "faces": []
        }
        if os.path.isfile(f):
            img = cv2.cvtColor(cv2.imread(f), cv2.COLOR_BGRA2BGR)
            faces = detector.detect_faces(img)
            holder['faces'] = faces
            for i, face in enumerate(holder['faces']):
                cropped_face = img[face['box'][1]:face['box'][1]+face['box'][3], face['box'][0]:face['box'][0]+face['box'][2]]
                cv2.imwrite(f + "_" + str(i) + "_face.jpg", cropped_face)
            scan.append(holder)

output_file.writelines(json.dumps(scan) + "\n")
output_file.close()
