import sqlite3
from pathlib import Path

# Path to user.db (inside database folder)
BASE_DIR = Path(__file__).resolve().parent.parent
USER_DB_PATH = BASE_DIR / "database" / "user.db"

# Ensure database folder exists
USER_DB_PATH.parent.mkdir(exist_ok=True)

conn = sqlite3.connect(USER_DB_PATH)
cur = conn.cursor()

# ------------------ USERS TABLE ------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
);
""")

# ------------------ QUERY CACHE TABLE ------------------
cur.execute("""
CREATE TABLE IF NOT EXISTS query_cache (
    cache_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sql_query TEXT UNIQUE,
    result_json TEXT,
    created_at TEXT
);
""")

# ------------------ SEED USERS ------------------
users = [
    (101, "ANU", "admin123", "ADMIN"),
    (102, "PRIYA", "staff123", "JUNIORDEV"),
    (103, "SANGU", "mgr123", "MANAGER"),
    (104, "DIVYA", "staff123", "INTERN"),
    (105, "SHERIN", "hr123", "HR"),
    (106, "AKSHARA", "staff123", "SENIORDEV"),
    (107, "ATHARVA", "staff123", "PROJECTMANAGER"),
    (108, "MAHA", "staff123", "TEAMLEAD"),
    (109, "PRASHEETHA", "staff123", "EMPLOYEE"),
    (110,"KAMALESH", "staff123", "ASSOCIATEENGINEER"),
    (111,"MEENA", "staff123", "ASSOCIATEENGINEER"),
    (112,"ABI", "staff123", "ASSOCIATEENGINEER"),
    (113,"DHEERAJ", "staff123", "ASSOCIATEENGINEER"),
    (114,"VIBHUDESH", "staff123", "ASSOCIATEENGINEER"),
    (115,"RAHUL", "staff123", "ASSOCIATEENGINEER"),
    
]


cur.executemany(
    "INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)",
    users
)

conn.commit()
conn.close()

print("✅ user.db initialized successfully")
