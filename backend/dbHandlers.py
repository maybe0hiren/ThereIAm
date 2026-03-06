import sqlite3
import uuid
import numpy as np
import cv2
from helpers import pHash

DB_PATH = "database/database.db"

def setup():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS UserTable (
            UserID TEXT PRIMARY KEY,
            UserName TEXT NOT NULL,
            Email TEXT UNIQUE NOT NULL,
            PasswordHash BLOB NOT NULL
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS UserFaceTable (
            UserID TEXT NOT NULL,
            FaceHash BLOB NOT NULL,
            FOREIGN KEY (UserID) REFERENCES UserTable(UserID)
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
            ImageID TEXT NOT NULL,
            HashValue BLOB NOT NULL,
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


def createUser(username: str, email: str, passwordHash: bytes):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT Email FROM UserTable WHERE Email=?", (email,))
    if cursor.fetchone():
        conn.close()
        raise ValueError("Email already exists")
    userId = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO UserTable (UserID, UserName, Email, PasswordHash) VALUES (?, ?, ?, ?)",
        (userId, username, email, passwordHash)
    )
    conn.commit()
    conn.close()
    return userId


def addUserEmbeddings(userId: str, embeddings: list):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO UserFaceTable (UserID, FaceHash) VALUES (?, ?)",
        [(userId, emb.tobytes()) for emb in embeddings]
    )
    conn.commit()
    conn.close()


def getUserByEmail(email: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT UserID, PasswordHash FROM UserTable WHERE Email=?",
        (email,)
    )
    row = cursor.fetchone()
    conn.close()
    return row


def getUserEmbeddings(userId: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT FaceHash FROM UserFaceTable WHERE UserID=?",
        (userId,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [np.frombuffer(row[0], dtype="float32") for row in rows]


def addImageToDB(imgPath: str, faceEmbeddings: list, classId: int):
    image = cv2.imread(str(imgPath))
    imageId = pHash(image)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO ImageTable (ImageID, ClassID, Address)
        VALUES (?, ?, ?)
    """, (imageId, classId, imgPath))
    cursor.executemany("""
        INSERT OR IGNORE INTO FaceHashTable (ImageID, HashValue)
        VALUES (?, ?)
    """, [(imageId, emb.tobytes()) for emb in faceEmbeddings])
    conn.commit()
    conn.close()
    return imageId


def getAllImageFaces():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT ImageID, HashValue FROM FaceHashTable")
    rows = cursor.fetchall()
    conn.close()
    return [(r[0], np.frombuffer(r[1], dtype="float32")) for r in rows]


def getImagePath(imageId: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT Address FROM ImageTable WHERE ImageID=?",
        (imageId,)
    )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


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