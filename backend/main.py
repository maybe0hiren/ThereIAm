from insightface.app import FaceAnalysis
from pathlib import Path
import cv2
import shutil

from helpers import generateEmbeddings
from imgProcessing.faceDetection import detectFaces
import dbHandlers
from userHandlers import registerUser
from userHandlers import loginUser
from userHandlers import findImages


embedder = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
embedder.prepare(ctx_id=-1)

def imgToDB(imagesFolder, classID):
    imagesFolder = Path(imagesFolder)
    if not imagesFolder.exists() or not imagesFolder.is_dir():
        raise ValueError("Class not available...")

    for imagePath in imagesFolder.iterdir():
        if imagePath.suffix.lower() not in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
            continue
        print("Processing ", imagePath, "...")
        image = cv2.imread(str(imagePath))
        if image is None or image.size == 0:
            continue
        verticesList = detectFaces(image)
        if not verticesList:
            continue
        faceHashList = []
        print("Generating Embeddings...")
        for vertices in verticesList:
            x_coords = [v[0] for v in vertices]
            y_coords = [v[1] for v in vertices]

            x1, x2 = max(0, min(x_coords)), min(image.shape[1], max(x_coords))
            y1, y2 = max(0, min(y_coords)), min(image.shape[0], max(y_coords))

            padding = 50
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(image.shape[1], x2 + padding)
            y2 = min(image.shape[0], y2 + padding)

            faceCrop = image[y1:y2, x1:x2]
            if faceCrop.size == 0:
                continue
            try:
                emb = generateEmbeddings(faceCrop, embedder)
                faceHashList.append(emb)
            except Exception as e:
                print(e)
                continue
        if faceHashList:
            dbHandlers.addImageToDB(str(imagePath), faceHashList, classID)


def registrationPipeline(imagesFolder, name, email, password, role):
    imagesFolder = Path(imagesFolder)
    if not imagesFolder.exists() or not imagesFolder.is_dir():
        raise ValueError("User image folder not available")
    userImages = []
    for imagePath in imagesFolder.iterdir():
        if imagePath.suffix.lower() not in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
            continue
        image = cv2.imread(str(imagePath))   
        if image is None or image.size == 0:
            continue
        image = cv2.resize(image, (640, 640))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.equalizeHist(cv2.cvtColor(image, cv2.COLOR_RGB2GRAY))
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        userImages.append(image)

    if not userImages:
        raise ValueError("No valid faces found for user registration")
    userID = registerUser(name, email, password, userImages, embedder, role)
    return userID


def loginPipeline(email, password):
    try:
        userID = loginUser(email, password)
        print("Login successful.")
        return userID
    except Exception as e:
        print("Login failed:", e)
        return None

def searchPipeline(userID, classCode):
    print("Entered search pipeline")
    try:
        classId = dbHandlers.getClassByCode(classCode)
        if not classId:
            raise ValueError("Invalid class code")

        images = findImages(userID, classId)
        return images

    except Exception as e:
        print("Search failed:", e)
        raise e

def deleteClassPipeline(classCode):
    print("Entered Delete Class Pipeline")
    try:
        classId = dbHandlers.getClassByCode(classCode)
        if not classId:
            raise ValueError("Invalid class code")
        dbHandlers.deleteClass(classId)
        shutil.rmtree(f"database/Images/{classCode}")

    except Exception as e:
        print("Deletion error: ", e)
        raise e