from flask import Flask, jsonify, request


from main import imgToDB


from pathlib import Path
import uuid
UPLOAD_DIR = Path("database/Images")
UPLOAD_DIR.mkdir(exist_ok=True)
app = Flask(__name__)
app.config["DEBUG"] = True



#Health Check
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "message": "Backend Live..."
    })

#Admin uploads a bunch of photos
@app.route("/admin/uploadPhotos", methods=["POST"])
def uploadPhotos():
    if "photos" not in request.files:
        return jsonify({"error" : "No photos uploaded"}), 400
    files = request.files.getlist("photos")
    savedImages = []
    for file in files:
        if file.filename == "":
            continue
        suffix = Path(file.filename).suffix.lower()
        filename = f"{uuid.uuid4().hex}{suffix}"
        filepath = UPLOAD_DIR / "dummyUser" / filename
        file.save(filepath)
        savedImages.append(str(filepath))
    imgToDB("database/Images/dummyUser", 12345)
    return jsonify({
        "count" : len(savedImages)
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)