import sqlite3
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
db_path = BASE_DIR / "database" / "user.db"

conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

cur.execute("SELECT * FROM users")
print(cur.fetchall())
