from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'library.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
