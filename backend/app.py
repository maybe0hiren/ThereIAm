from flask import Flask, jsonify, request
from pathlib import Path
import uuid

from main import imgToDB, registrationPipeline, loginPipeline, searchPipeline

UPLOAD_DIR = Path("database/Images")
UPLOAD_DIR.mkdir(exist_ok=True)

USER_UPLOAD_DIR = UPLOAD_DIR / "users"
USER_UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["DEBUG"] = True


# Health Check
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "message": "Backend Live..."
    })



@app.route("/admin/uploadPhotos", methods=["POST"])
def uploadPhotos():
    if "photos" not in request.files:
        return jsonify({"error": "No photos uploaded"}), 400
    files = request.files.getlist("photos")
    datasetFolder = UPLOAD_DIR / "dataset"
    datasetFolder.mkdir(exist_ok=True)
    savedImages = []
    for file in files:
        if file.filename == "":
            continue
        suffix = Path(file.filename).suffix.lower()
        filename = f"{uuid.uuid4().hex}{suffix}"
        filepath = datasetFolder / filename
        file.save(filepath)
        savedImages.append(str(filepath))
    imgToDB(datasetFolder, 12345)
    return jsonify({
        "count": len(savedImages)
    }), 200


@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    if not name or not email or not password:
        return jsonify({"error": "Missing fields"}), 400
    if "photos" not in request.files:
        return jsonify({"error": "No face images provided"}), 400
    files = request.files.getlist("photos")
    userFolder = USER_UPLOAD_DIR / uuid.uuid4().hex
    userFolder.mkdir(exist_ok=True)
    for file in files:
        suffix = Path(file.filename).suffix.lower()
        filename = f"{uuid.uuid4().hex}{suffix}"
        filepath = userFolder / filename
        file.save(filepath)
    try:
        userID = registrationPipeline(userFolder, name, email, password)
        return jsonify({
            "status": "registered",
            "userID": userID
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400



@app.route("/login", methods=["POST"])
def login():

    data = request.json

    email = data.get("email")
    password = data.get("password")

    try:
        userID = loginPipeline(email, password)

        return jsonify({
            "status": "login_success",
            "userID": userID
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 401



@app.route("/search", methods=["POST"])
def search():

    data = request.json
    userID = data.get("userID")

    if not userID:
        return jsonify({"error": "Missing userID"}), 400

    try:
        images = searchPipeline(userID)

        return jsonify({
            "count": len(images),
            "images": images
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)