import jwt
import datetime
from functools import wraps

from flask import Flask, jsonify, request
from pathlib import Path
import uuid
from flask import send_from_directory
from flask_cors import CORS

from main import imgToDB, registrationPipeline, loginPipeline, searchPipeline

UPLOAD_DIR = Path("database/Images")
UPLOAD_DIR.mkdir(exist_ok=True)

USER_UPLOAD_DIR = UPLOAD_DIR / "users"
USER_UPLOAD_DIR.mkdir(exist_ok=True)

SECRET_KEY = "DFGFGcvbhjgft65e44567uifd"

app = Flask(__name__)
app.config["DEBUG"] = True

CORS(app)


# Health Check
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "message": "Backend Live..."
    })


def tokenRequired(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        authHeader = request.headers.get("Authorization")
        if not authHeader:
            return jsonify({"error" : "Token missing"}), 401
        try:
            token = authHeader.split(" ")[1]
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            userID = data["userID"]
        except Exception:
            return jsonify({"error" : "Invalid token"}), 401
        return f(userID, *args, **kwargs)
    return decorated


@app.route("/admin/uploadPhotos", methods=["POST"])
@tokenRequired
def uploadPhotos(userID):
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

        token = jwt.encode({
            "userID" : userID,
            "exp" : datetime.datetime.utcnow() + datetime.timedelta(hours=12)
        }, SECRET_KEY, algorithm="HS256")

        return jsonify({
            "status": "login_success",
            "token": token
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 401



@app.route("/search", methods=["POST"])
@tokenRequired
def search(userID):
    try:
        images = searchPipeline(userID)

        return jsonify({
            "count": len(images),
            "images": images
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/images/<path:filename>")
def serveImage(filename):
    return send_from_directory("database/Images", filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)