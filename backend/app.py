from flask import Flask, request, jsonify
from flask_cors import CORS

import tempfile

import insightface
import cv2
import numpy as np


app = Flask(__name__)
CORS(app)

detector = insightface.app.FaceAnalysis(providers=['CPUExecutionProvider'])
detector.prepare(ctx_id=0, det_size=(640,640))
def detectFaces(image_input):
    if isinstance(image_input, str):
        img = cv2.imread(image_input)
        if img is None:
            raise ValueError(f"Could not read image from path: {image_input}")
    else:
        img = image_input

    faces = detector.get(img)
    results = [face.bbox.astype(int).tolist() for face in faces]
    return results
def cropping(videoSnaps):
    croppedSnaps = []
    for i, img in enumerate(videoSnaps):
        boxes = detectFaces(img)
        if not boxes:
            print(f"No faces found in frame {i}")
            continue
        x1, x2, y1, y2 = boxes[0]
        faceCrop = img[y1:y2, x1:x2]
        faceCrop = cv2.resize(faceCrop, (160, 160))
        croppedSnaps.append(faceCrop)
    return croppedSnaps
embedder = insightface.app.FaceAnalysis(providers=['CPUExecutionProvider'])
embedder.prepare(ctx_id=0, det_size=(640, 640))
def getHashes(videoSnaps):
    if not videoSnaps:
        raise ValueError("No faces provided")
    embeddings = []
    for i, face in enumerate(videoSnaps):
        faces = embedder.get(face)
        if not faces:
            print(f"No face in provided image {i}")
            continue
        embedding = faces[0].embedding
        embeddings.append(embedding)
    if not embeddings:
        raise ValueError("No embeddings computable")
    embeddings = np.array(embeddings)
    finalHash = np.mean(embeddings, axis=0)
    finalHash = finalHash/np.linalg.norm(finalHash)
    return finalHash




@app.route("/", methods=["GET"])
def index():
    return "✅ InsightFace API is running!"


userVideo = None
videoSnaps = []
@app.route("/registration", methods=["POST"])
def registration():
    global userVideo
    video = request.files.get("video")
    if not video:
        return jsonify({"error":"No video received"}), 400
    userVideo = video.read()
    with tempfile.NamedTemporaryFile(delete=True, suffix=".mp4") as tempVideo:
        tempVideo.write(userVideo)
        tempVideo.flush()
        capture = cv2.VideoCapture(tempVideo.name)
        videoSnaps = []
        frameCount = 0
        success, frame = capture.read()
        while success:
            if frameCount%30 == 0:
                videoSnaps.append(frame)
            frameCount += 1
            success, frame = capture.read()
        capture.release()
        videoSnaps = cropping(videoSnaps=videoSnaps)
        faceHash = getHashes(videoSnaps=videoSnaps)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)