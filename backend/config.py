import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "database" / "text_to_sql.db"
USER_DB_PATH = BASE_DIR / "database" / "user.db"

OPENROUTER_API_KEY = "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"
OPENROUTER_MODEL = "gpt-4o-mini"
