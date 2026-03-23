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
            PasswordHash BLOB NOT NULL,
            Role TEXT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS UserFaceTable (
            UserID TEXT NOT NULL,
            FaceHash BLOB NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ClassTable (
            ClassID TEXT PRIMARY KEY,
            ClassName TEXT NOT NULL,
            ClassCode TEXT UNIQUE NOT NULL,
            AdminID TEXT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ImageTable (
            ImageID TEXT PRIMARY KEY,
            ClassID TEXT,
            Address TEXT UNIQUE NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS FaceHashTable (
            ImageID TEXT NOT NULL,
            HashValue BLOB NOT NULL,
            PRIMARY KEY (ImageID, HashValue)
        );
    """)

    conn.commit()
    conn.close()


def createUser(username, email, passwordHash, role="member"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT Email FROM UserTable WHERE Email=?", (email,))
    if cursor.fetchone():
        conn.close()
        raise ValueError("Email already exists")

    userId = str(uuid.uuid4())

    cursor.execute("""
        INSERT INTO UserTable (UserID, UserName, Email, PasswordHash, Role)
        VALUES (?, ?, ?, ?, ?)
    """, (userId, username, email, passwordHash, role))

    conn.commit()
    conn.close()
    return userId


def addUserEmbeddings(userId, embeddings):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executemany(
        "INSERT INTO UserFaceTable (UserID, FaceHash) VALUES (?, ?)",
        [(userId, emb.tobytes()) for emb in embeddings]
    )

    conn.commit()
    conn.close()


def getUserByEmail(email):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT UserID, PasswordHash, Role FROM UserTable WHERE Email=?
    """, (email,))

    row = cursor.fetchone()
    conn.close()
    return row


def getUserEmbeddings(userId):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT FaceHash FROM UserFaceTable WHERE UserID=?",
        (userId,)
    )

    rows = cursor.fetchall()
    conn.close()

    return [np.frombuffer(r[0], dtype="float32") for r in rows]


def createClass(adminId, className, classCode):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    classId = str(uuid.uuid4())

    cursor.execute("""
        INSERT INTO ClassTable (ClassID, ClassName, ClassCode, AdminID)
        VALUES (?, ?, ?, ?)
    """, (classId, className, classCode, adminId))

    conn.commit()
    conn.close()
    return classId


def getClassByCode(classCode):
    print("Entered GetClassByCode")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ClassID FROM ClassTable WHERE ClassCode=?
    """, (classCode,))

    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def addImageToDB(imgPath, faceEmbeddings, classId):
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


def getAllImageFacesByClass(classId):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT f.ImageID, f.HashValue
        FROM FaceHashTable f
        JOIN ImageTable i ON f.ImageID = i.ImageID
        WHERE i.ClassID=?
    """, (classId,))

    rows = cursor.fetchall()
    conn.close()

    return [(r[0], np.frombuffer(r[1], dtype="float32")) for r in rows]


def getImagePath(imageId):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT Address FROM ImageTable WHERE ImageID=?", (imageId,))
    row = cursor.fetchone()

    conn.close()
    return (row[0]).replace("database/Images/", "") if row else None

def getClassesByAdmin(adminId):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ClassName, ClassCode FROM ClassTable WHERE AdminID=?
    """, (adminId,))

    rows = cursor.fetchall()
    conn.close()

    return [{"name": r[0], "code": r[1]} for r in rows]

def deleteClass(classId):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ImageTable WHERE ClassID=?", (classId,))
    cursor.execute("DELETE FROM ClassTable WHERE ClassID=?", (classId,))

    conn.commit()
    conn.close()


def returnClassImages(classID):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ImageID, Address 
        FROM ImageTable
        WHERE ClassID = ?
    """, (classID,))
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "path": row[1].replace("database/Images/", "")
        }
        for row in rows
    ]


def deleteImage(imageId):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM FaceHashTable WHERE ImageID=?",
        (imageId,)
    )
    cursor.execute(
        "DELETE FROM ImageTable WHERE ImageID=?",
        (imageId,)
    )
    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup()