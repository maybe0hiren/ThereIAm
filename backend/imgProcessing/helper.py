import numpy as np

def generateCrops(image: np.ndarray, verticesGroup):
    if image is None or image.size == 0:
        raise ValueError("Imvalid Image")
    
    h, w = image.shape[:2]
    crops = []

    for vertices in verticesGroup:
        if len(vertices) != 4:
            continue
        xs = [v[0] for v in vertices]
        ys = [v[1] for v in vertices]
        x1 = max(min(xs) - padding, 0)
        y1 = max(min(ys) - padding, 0)
        x2 = min(max(xs) + padding, w)
        y2 = min(max(ys) + padding, h)
        if x2 <= x1 or y2 <= y1:
            continue
        crop = image[y1:y2, x1:x2]
        crops.append(crop)
    return crops


def generateEmbeddings(image, embedder):
    if image is None or image.size == 0:
        raise ValueError("Invalid Image")
    faces = embedder.get(image)
    if not faces:
        raise ValueError("No faces detected...")
    emb = faces[0].embedding
    return (emb / np.linalg.norm(emb)).astype("float32")
