from flask import Flask, request, jsonify
from flask_cors import CORS
import base64

import insightface
import cv2
import numpy as np


app = Flask(__name__)
CORS(app)

detector = insightface.app.FaceAnalysis(providers=['CPUExecutionProvider'])
detector.prepare(ctx_id=0, det_size=(640,640))


@app.route("/detect", methods=["POST"])
def detectFaces():
    if 'image' not in request.files:
        return jsonify({"error": "No images uploaded"}), 400
    
    file = request.files["image"]
    image_bytes = file.read()
    npimg = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    faces = detector.get(img)
    results = []
    for face in faces:
        bbox = face.bbox.astype(int).tolist()
        results.append(bbox)
        cv2.rectangle(img, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
    _, buffer = cv2.imencode('.jpg', img)
    encodedImage = base64.b64encode(buffer).decode('utf-8')
    return jsonify({"faces": results, "marked_image":encodedImage})

@app.route("/", methods=["GET"])
def index():
    return "✅ InsightFace API is running!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)