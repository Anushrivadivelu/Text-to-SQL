import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "database" / "text_to_sql.db"
USER_DB_PATH = BASE_DIR / "database" / "user.db"

OPENROUTER_API_KEY ="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"
OPENROUTER_MODEL = "gpt-4o-mini"

