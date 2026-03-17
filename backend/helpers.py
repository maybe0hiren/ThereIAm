import numpy as np
import cv2


def generateEmbeddings(image, embedder):
    if image is None or image.size == 0:
        raise ValueError("Invalid Image")
    faces = embedder.get(image)
    print("Faces from embedder:", len(faces) if faces else 0)
    if not faces:
        raise ValueError("No faces detected...")
    emb = faces[0].embedding
    return (emb / np.linalg.norm(emb)).astype("float32")


def pHash(image, hash_size=32) -> str:
    if image is None or image.size == 0:
        raise ValueError("Invalid image")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    size = hash_size * 4
    resized = cv2.resize(gray, (size, size), interpolation=cv2.INTER_AREA)
    dct = cv2.dct(np.float32(resized))
    dct_low = dct[:hash_size, :hash_size]
    med = np.median(dct_low[1:, 1:])
    diff = dct_low > med
    bit_string = ''.join('1' if v else '0' for v in diff.flatten())
    return f"{int(bit_string, 2):016x}"