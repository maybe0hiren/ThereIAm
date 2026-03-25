import bcrypt
import cv2
import numpy as np
from helpers import generateEmbeddings
import dbHandlers
import faissHandler


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


def findImages(friendIDs, userID, classId, threshold=0.2):
    print("Entered Find Images")
    memberEmbeddings = []
    userEmbeddings = dbHandlers.getUserEmbeddings(userID)
    if userEmbeddings:
        memberEmbeddings.append(userEmbeddings)
        print(f"User Embeddings Count: {len(userEmbeddings)}")
    else:
        print("User Embeddings Count: 0")
    
    for friendID in (friendIDs or []):
        friendEmbeddings = dbHandlers.getUserEmbeddings(friendID)
        if friendEmbeddings:
            memberEmbeddings.append(friendEmbeddings)
            print(f"Friend Embeddings Count: {len(friendEmbeddings)}")
        else:
            print("Friend Embeddings Count: 0")

    dbFaces = dbHandlers.getAllImageFacesByClass(classId)
    print(f"Total Faces in Class: {len(dbFaces) if dbFaces else 0}")

    if not memberEmbeddings or not dbFaces:
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
    userMatrices = []
    for memberEmbedding in memberEmbeddings:
        userMatrix = np.array(memberEmbedding)
        userMatrices.append(userMatrix)

    imageMatchMap = {}

    for memberIdx, userMatrix in enumerate(userMatrices):
        print(f"\nProcessing member {memberIdx}...")

        for emb in userMatrix:
            matchedImageIDs = faissHandler.search(emb, k=20)

            for imgID in matchedImageIDs:
                if imgID not in imageMatchMap:
                    imageMatchMap[imgID] = set()

                imageMatchMap[imgID].add(memberIdx)
    print(f"Image Match Map: {imageMatchMap}")
    
    
    requiredMembers = len(userMatrices)
    finalMatches = [
        imgID for imgID, matchedMembers in imageMatchMap.items()
        if len(matchedMembers) == requiredMembers
    ]

    print(f"Final AND Matches: {finalMatches}")

    result = []
    for imageID in finalMatches:
        path = dbHandlers.getImagePath(imageID)

        if path:
            result.append({
                "id": imageID,
                "path": path
            })

    print(f"Final Images: {result}")

    return result