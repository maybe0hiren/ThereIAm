import faiss
import numpy as np
import dbHandlers

index = None
idMap = []

DIM = 512


def buildIndex():
    global index, idMap

    print("Building FAISS index...")

    allFaces = dbHandlers.getAllImageFacesByClassGlobal()

    if not allFaces:
        print("No embeddings found. Skipping FAISS build.")
        index = faiss.IndexFlatIP(DIM)
        idMap = []
        return

    embeddings = []
    idMap = []

    for imgID, emb in allFaces:
        embeddings.append(emb)
        idMap.append(imgID)

    embeddings = np.array(embeddings).astype("float32")

    index = faiss.IndexFlatIP(DIM)
    index.add(embeddings)

    print(f"FAISS index built with {len(idMap)} vectors")


def addEmbeddings(imageID, embeddings):
    global index, idMap

    if index is None:
        buildIndex()

    vecs = np.array(embeddings).astype("float32")

    index.add(vecs)

    for _ in embeddings:
        idMap.append(imageID)


def search(queryEmbedding, k=10):
    global index, idMap

    if index is None or index.ntotal == 0:
        return []

    query = np.array([queryEmbedding]).astype("float32")

    distances, indices = index.search(query, k)

    results = []

    for idx in indices[0]:
        if idx == -1:
            continue
        results.append(idMap[idx])

    return results


def removeImage(imageID):
    print(f"Rebuilding FAISS index after deletion of {imageID}")
    buildIndex()