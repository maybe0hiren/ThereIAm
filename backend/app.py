import jwt
import datetime
from functools import wraps

from flask import Flask, jsonify, request, send_from_directory
from pathlib import Path
import uuid
from flask_cors import CORS

from main import imgToDB, registrationPipeline, loginPipeline, searchPipeline, deleteClassPipeline, getAllImages
import dbHandlers

UPLOAD_DIR = Path("database/Images")
UPLOAD_DIR.mkdir(exist_ok=True)

USER_UPLOAD_DIR = UPLOAD_DIR / "users"
USER_UPLOAD_DIR.mkdir(exist_ok=True)

SECRET_KEY = "DFGFGcvbhjgft65e44567uifd"

app = Flask(__name__)
app.config["DEBUG"] = True

CORS(app)


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
            return jsonify({"error": "Token missing"}), 401

        try:
            token = authHeader.split(" ")[1]
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

            userID = data["userID"]
            role = data["role"]

        except Exception:
            return jsonify({"error": "Invalid token"}), 401

        return f(userID, role, *args, **kwargs)

    return decorated


def adminRequired(f):
    @wraps(f)
    def decorated(userID, role, *args, **kwargs):
        if role != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return f(userID, role, *args, **kwargs)
    return decorated



@app.route("/admin/createClass", methods=["POST"])
@tokenRequired
@adminRequired
def createClassRoute(userID, role):
    data = request.json
    className = data.get("className")

    if not className:
        return jsonify({"error": "Class name required"}), 400

    classCode = uuid.uuid4().hex[:6].upper()

    dbHandlers.createClass(userID, className, classCode)

    return jsonify({
        "classCode": classCode
    })


@app.route("/admin/uploadPhotos", methods=["POST"])
@tokenRequired
@adminRequired
def uploadPhotos(userID, role):

    classCode = request.form.get("classCode")

    classId = dbHandlers.getClassByCode(classCode)
    if not classId:
        return jsonify({"error": "Invalid class code"}), 400

    if "photos" not in request.files:
        return jsonify({"error": "No photos uploaded"}), 400

    files = request.files.getlist("photos")

    datasetFolder = UPLOAD_DIR / classCode
    datasetFolder.mkdir(exist_ok=True)

    savedImages = []

    for file in files:
        suffix = Path(file.filename).suffix.lower()
        filename = f"{uuid.uuid4().hex}{suffix}"
        filepath = datasetFolder / filename

        file.save(filepath)
        savedImages.append(str(filepath))

    imgToDB(datasetFolder, classId)

    return jsonify({
        "count": len(savedImages)
    })

@app.route("/admin/classes", methods=["GET"])
@tokenRequired
@adminRequired
def getAdminClasses(userID, role):
    classes = dbHandlers.getClassesByAdmin(userID)
    return jsonify({"classes": classes})


@app.route("/admin/getAllImages", methods=["POST"])
@tokenRequired
@adminRequired
def getAllImagesFromClass(userID, classCode):
    print("GetAllImages Endpoint called")
    data = request.json
    classCode = data.get("classCode")
    if not classCode:
        return jsonify({"error": "Class code required"}), 400
    try:
        images = getAllImages(classCode)
        return jsonify({"images": images})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    role = request.form.get("role") or "member"

    if not name or not email or not password:
        return jsonify({"error": "Missing fields"}), 400

    if "photos" not in request.files:
        return jsonify({"error": "No face images provided"}), 400

    files = request.files.getlist("photos")

    userFolder = USER_UPLOAD_DIR / uuid.uuid4().hex
    userFolder.mkdir(exist_ok=True)

    for file in files:
        filename = f"{uuid.uuid4().hex}.jpg"
        file.save(userFolder / filename)

    try:
        userID = registrationPipeline(userFolder, name, email, password, role)

        return jsonify({
            "userID": userID,
            "role": role
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/login", methods=["POST"])
def login():
    data = request.json

    email = data.get("email")
    password = data.get("password")

    try:
        userID, role = loginPipeline(email, password)

        token = jwt.encode({
            "userID": userID,
            "role": role,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12)
        }, SECRET_KEY, algorithm="HS256")

        return jsonify({
            "token": token,
            "role": role
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 401



@app.route("/search", methods=["POST"])
@tokenRequired
def search(userID, role):
    print("Search Endpoint called")
    data = request.json
    classCode = data.get("classCode")

    if not classCode:
        return jsonify({"error": "Class code required"}), 400

    try:
        images = searchPipeline(userID, classCode)

        return jsonify({
            "images": images
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/deleteClass", methods=["POST"])
@tokenRequired
@adminRequired
def deleteClass(userID, role):
    data = request.json
    classCode = data.get("classCode")
    if not classCode:
        return jsonify({"error": "Class code required"}), 400

    try:
        deleteClassPipeline(classCode)
        return jsonify({
            "status": "ok"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/images/<path:filename>")
def serveImage(filename):
    return send_from_directory("database/Images", filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)