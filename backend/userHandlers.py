import bcrypt
import cv2
import numpy as np
from helpers import generateEmbeddings
import dbHandlers


def registerUser(name, email, password, images, embedder, role="member"):
    passwordHash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    userID = dbHandlers.createUser(name, email, passwordHash, role)

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

    userID, passwordHash, role = row

    if not bcrypt.checkpw(password.encode(), passwordHash):
        raise ValueError("Wrong Password")

    return userID, role


def findImages(userID, classId, threshold=0.2):
    print("Entered Find Images")

    userEmbeddings = dbHandlers.getUserEmbeddings(userID)
    print(f"User Embeddings Count: {len(userEmbeddings) if userEmbeddings else 0}")

    dbFaces = dbHandlers.getAllImageFacesByClass(classId)
    print(f"Total Faces in Class: {len(dbFaces) if dbFaces else 0}")

    if not userEmbeddings or not dbFaces:
        print("No embeddings or no faces found. Returning empty list.")
        return []

    imageIDs = []
    faceEmbeddings = []

    print("Separating image IDs and embeddings...")
    for imgID, emb in dbFaces:
        imageIDs.append(imgID)
        faceEmbeddings.append(emb)

    print(f"Collected {len(faceEmbeddings)} face embeddings")

    datasetMatrix = np.array(faceEmbeddings)
    userMatrix = np.array(userEmbeddings)

    print(f"Dataset Matrix Shape: {datasetMatrix.shape}")
    print(f"User Matrix Shape: {userMatrix.shape}")

    similarityMatrix = datasetMatrix @ userMatrix.T
    maxSimilarity = similarityMatrix.max(axis=1)
    matches = set()

    print(f"Applying threshold: {threshold}")
    for idx, sim in enumerate(maxSimilarity):
        print(f"Face {idx}: Similarity = {sim}")
        if sim >= threshold:
            print("Image found")
            matches.add(imageIDs[idx])

    print(f"Matched Image IDs: {matches}")

    result = []

    for imageID in matches:
        path = dbHandlers.getImagePath(imageID)

        if path:
            result.append({
                "id": imageID,
                "path": path
            })

    print(f"Final Images: {result}")

    return result