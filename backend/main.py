from insightface.app import FaceAnalysis
from pathlib import Path
import cv2
import numpy as np

from imgProcessing.faceDetection import detectFaces
from database.dbHandlers import addImageToDB


#Create an embedder
embedder = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
embedder.prepare(ctx_id=-1)


def generateEmbeddings(image, embedder):
    if image is None or image.size == 0:
        raise ValueError("Invalid Image")
    faces = embedder.get(image)
    if not faces:
        raise ValueError("No faces detected...")
    emb = faces[0].embedding
    return (emb / np.linalg.norm(emb)).astype("float32")

#Image to Embddings in DB pipeline
def imgToDB(imagesFolder, classID):
    #Setup the folder
    imagesFolder = Path(imagesFolder)
    if not imagesFolder.exists() or not imagesFolder.is_dir():
        raise ValueError("Class not available...")

    #Handle images in the folder
    for imagePath in imagesFolder.iterdir():
        if imagePath.suffix.lower() not in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
            continue
        print(imagePath)
        image = cv2.imread(str(imagePath))
        if image is None or image.size == 0:
            continue
        verticesList = detectFaces(image)
        print("Vertices list: ", verticesList)
        if not verticesList:
            continue
        faceHashList = []
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
                print("Embeddings: ", emb)
                faceHashList.append(emb)
            except Exception as e:
                print(e)
                continue
        if faceHashList:
            addImageToDB(str(imagePath), faceHashList, classID)

if __name__ == "__main__":
    imgToDB("database/Images/dummyUser", 1234)