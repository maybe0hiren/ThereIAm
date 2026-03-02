import sqlite3
from insightface.app import FaceAnalysis
import cv2


from helpers import pHash

DB_PATH = "database/database.db"

embedder = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
embedder.prepare(ctx_id=-1)

def setup():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS UserTable (
            UserID TEXT PRIMARY KEY,
            UserName TEXT NOT NULL,
            Email TEXT UNIQUE NOT NULL,
            PasswordHash TEXT NOT NULL,
            FaceHash TEXT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ImageTable (
            ImageID TEXT PRIMARY KEY,
            ClassID INTEGER,
            Address TEXT UNIQUE NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS FaceHashTable (
            ImageID INTEGER NOT NULL,
            HashValue TEXT NOT NULL,
            PRIMARY KEY (ImageID, HashValue),
            FOREIGN KEY (ImageID) REFERENCES ImageTable(ImageID)
        );
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_hashvalue
        ON FaceHashTable(HashValue);
    """)

    conn.commit()
    conn.close()
    print("Setup completed.")

def addImageToDB(imgAdd: str, faceHashList: list, classID: int):
    image = cv2.imread(str(imgAdd))
    image_id = pHash(image)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO ImageTable (ImageID, ClassID, Address)
        VALUES (?, ?, ?)
    """, (image_id, classID, imgAdd))

    cursor.executemany("""
        INSERT OR IGNORE INTO FaceHashTable (ImageID, HashValue)
        VALUES (?, ?)
    """, [(image_id, emb.tobytes()) for emb in faceHashList])

    conn.commit()
    conn.close()
    print("Image data inserted in DB")


def getImagesFromDB(faceHashList: list):
    if not faceHashList:
        return []

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    placeholders = ",".join("?" for _ in faceHashList)

    cursor.execute(f"""
        SELECT i.Address
        FROM ImageTable i
        JOIN FaceHashTable f ON i.ImageID = f.ImageID
        WHERE f.HashValue IN ({placeholders})
        GROUP BY i.ImageID
        HAVING COUNT(DISTINCT f.HashValue) = ?
    """, (*faceHashList, len(faceHashList)))

    results = [row[0] for row in cursor.fetchall()]
    conn.close()
    return results


if __name__ == "__main__":
    setup()