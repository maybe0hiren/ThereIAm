import bcrypt
import cv2
import numpy as np  
from helpers import generateEmbeddings
import dbHandlers


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
    matches = set()
    for imageID, faceEmb in dbFaces:
        for u_emb in userEmbeddings:
            sim = np.dot(u_emb, faceEmb)
            if sim >= threshold:
                matches.add(imageID)
                break
    return [dbHandlers.getImagePath(i) for i in matches]