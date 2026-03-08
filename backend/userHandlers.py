import bcrypt
import cv2
import numpy as np
from helpers import generateEmbeddings
import dbHandlersc


def registerUser(name, email, password, images, embedder):
    passwordHash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    userID = dbHandlers.createUser(name, email, passwordHash)
    embeddings = []
    for img in images:
        image = cv2.imread(img) if isinstance(img, str) else img
        emb = generateEmbeddings(image, embedder)
        embeddings.append(emb)
    dbHandlers.addUserEmbeddings(userID, embeddings)
    return userID


def loginUser(email, password):
    row = dbHandlers.getUserByEmail(email)
    if not row:
        raise ValueError("User not found")
    userID, passwordHash = row
    if not bcrypt.checkpw(password.encode(), passwordHash):
        raise ValueError("Wrong Password")
    return userID


def findImages(userID, threshold=0.5):
    userEmbeddings = dbHandlers.getUserEmbeddings(userID)
    dbFaces = dbHandlers.getAllImageFaces()
    if not userEmbeddings or not dbFaces:
        return []
    imageIDs = []
    faceEmbeddings = []
    for imgID, emb in dbFaces:
        imageIDs.append(imgID)
        faceEmbeddings.append(emb)
    datasetMatrix = np.array(faceEmbeddings)
    userMatrix = np.array(userEmbeddings)
    similarityMatrix = datasetMatrix @ userMatrix.T
    maxSimilarity = similarityMatrix.max(axis=1)
    matches = set()
    for idx, sim in enumerate(maxSimilarity):
        if sim >= threshold:
            matches.add(imageIDs[idx])
    return [dbHandlers.getImagePath(i) for i in matches]