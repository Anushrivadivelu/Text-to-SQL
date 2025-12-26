import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "text_to_sql.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# ------------------ TABLES ------------------

cur.execute("""
CREATE TABLE IF NOT EXISTS departments (
    dept_id INTEGER PRIMARY KEY,
    dept_name TEXT UNIQUE
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS employees (
    emp_id INTEGER PRIMARY KEY,
    emp_name TEXT,
    dept_id INTEGER,
    salary INTEGER,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
);
""")

# ------------------ SEED DATA ------------------

departments = [
    (1, "ADMIN"),
    (2, "ENGINEERING"),
    (3, "MANAGEMENT"),
    (4, "HR"),
    (5, "GENERAL")
]

cur.executemany(
    "INSERT OR IGNORE INTO departments VALUES (?, ?)",
    departments
    
)

employees = [
    (101, "ANU", 1, 80000),
    (102, "PRIYA", 2, 50000),
    (103, "SANGU", 3, 90000),
    (104, "DIVYA", 2, 30000),
    (105, "SHERIN", 4, 45000),
    (106, "AKSHARA", 2, 70000),
    (107, "ATHARVA", 3, 95000),
    (108, "MAHA", 3, 85000),
    (109, "PRASHEETHA", 5, 35000),
    (110, "KAMALESH", 1, 40000),
    (111, "MEENA", 1, 42000),
    (112, "ABI", 2, 38000),
    (113, "DHEERAJ", 2, 39000),
    (114, "VIBHUDEESH", 1, 41000),
    (115, "RAHUL", 1, 43000),
    
]

cur.executemany(
    "INSERT OR IGNORE INTO employees VALUES (?, ?, ?, ?)",
    employees
)

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


print("Database initialized safely")
