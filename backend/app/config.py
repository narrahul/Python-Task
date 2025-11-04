from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def _default_sqlite_uri() -> str:
    default_path = Path(os.environ.get("DATABASE_FILE", "/tmp/library.db"))
    if not default_path.is_absolute():
        default_path = BASE_DIR / default_path
    default_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{default_path}"

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", _default_sqlite_uri())
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
