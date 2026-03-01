from insightface.app import FaceAnalysis
from pathlib import Path
import cv2


from imgProcessing.faceDetection import detectFaces
from imgProcessing.helper import generateCrops, generateEmbeddings
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
        image = cv2.imread(str(imagePath))
        if image is None:
            continue
        
        #PIPELINE

        #Get vertices around faces in an image
        vertices = detectFaces(image)
        if not vertices:
            continue
        #Get cropped images around the faces
        crops = generateCrops(image, vertices)
        if not crops:
            continue
        #Get a list of face embeddings
        embeddingsList = []
        for croppedImage in crops:
            embeddings = generateEmbeddings(croppedImage, embedder)
            embeddingsList.append(embeddings)
        #Add images and embeddings to the DB
        addImageToDB(str(imagePath), embeddingsList, classID)