
import sqlite3
from pathlib import Path

db = Path("database/user.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

cur.execute("SELECT * FROM users")
print(cur.fetchall())
