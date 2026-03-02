from insightface.app import FaceAnalysis
from pathlib import Path
import cv2


from helpers import generateEmbeddings
from imgProcessing.faceDetection import detectFaces
from database.dbHandlers import addImageToDB


#Create an embedder
embedder = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
embedder.prepare(ctx_id=-1)

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
            addImageToDB(str(imagePath), faceHashList, classID)

if __name__ == "__main__":
    imgToDB("database/Images/dummyUser", 1234)