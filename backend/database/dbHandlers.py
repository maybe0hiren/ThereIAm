import sqlite3

DB_PATH = "database/database.db"

def setup():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # User table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS UserTable (
            UserID TEXT PRIMARY KEY,
            UserName TEXT NOT NULL,
            Email TEXT UNIQUE NOT NULL,
            PasswordHash TEXT NOT NULL,
            FaceHash TEXT NOT NULL
        );
    """)
    # Image table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ImageTable (
            ImageID INTEGER PRIMARY KEY AUTOINCREMENT,
            ClassID INTEGER,
            Address TEXT UNIQUE NOT NULL
        );
    """)
    # Facehash table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS FaceHashTable (
            ImageID INTEGER NOT NULL,
            HashValue TEXT NOT NULL,
            PRIMARY KEY (ImageID, HashValue),
            FOREIGN KEY (ImageID) REFERENCES ImageTable(ImageID)
        );
    """)
    #Indexing 
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_hashvalue
        ON FaceHashTable(HashValue);
    """)

    conn.commit()
    conn.close()
    print("Setup completed.")


def addImageToDB(imgAdd: str, faceHashList: list, classID: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Insert image
    cursor.execute("""
        INSERT INTO ImageTable (ClassID, Address)
        VALUES (?, ?)
    """, (classID, imgAdd))

    image_id = cursor.lastrowid

    # Insert hashes
    cursor.executemany("""
        INSERT INTO FaceHashTable (ImageID, HashValue)
        VALUES (?, ?)
    """, [(image_id, h) for h in faceHashList])

    conn.commit()
    conn.close()
    print("Image entry successful.")


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


def addImageToDB(imgAdd: str, faceHashList: list, classID: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Insert image
    cursor.execute("""
        INSERT INTO ImageTable (ClassID, Address)
        VALUES (?, ?)
    """, (classID, imgAdd))

    image_id = cursor.lastrowid

    # Insert hashes
    cursor.executemany("""
        INSERT INTO FaceHashTable (ImageID, HashValue)
        VALUES (?, ?)
    """, [(image_id, h) for h in faceHashList])

    conn.commit()
    conn.close()
    print("Image entry successful.")


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