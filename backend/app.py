import insightface
import cv2
import numpy as np


detector = insightface.app.FaceAnalysis(providers=['CPUExecutionProvider'])  # or GPUExecutionProvider
detector.prepare(ctx_id=0, det_size=(640,640))


imageName = "face4"
img = cv2.imread(f"faces/{imageName}.jpeg")
faces = detector.get(img)


result = []
for face in faces:
    bbox = face['bbox']
    vertices = [
        (int(bbox[0]), int(bbox[1])),        # top-left
        (int(bbox[2]), int(bbox[1])),        # top-right
        (int(bbox[2]), int(bbox[3])),        # bottom-right
        (int(bbox[0]), int(bbox[3]))         # bottom-left
    ]

    for v in vertices:
        cv2.circle(img, v, radius=6, color=(0, 255, 0), thickness=-1)  # Green dot
    result.append(vertices)

cv2.imwrite(f"faces/{imageName}_marked.jpeg", img)  # Save the result
print(result)