import sqlite3, json
from datetime import datetime
from backend.config import USER_DB_PATH

def get_cached_result(sql):
    conn = sqlite3.connect(USER_DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT result_json FROM query_cache WHERE sql_query=?", (sql,))
    row = cur.fetchone()
    conn.close()
    return json.loads(row[0]) if row else None


def store_cached_result(sql, result):
    conn = sqlite3.connect(USER_DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO query_cache VALUES (NULL,?,?,?)",
        (sql, json.dumps(result), datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()
