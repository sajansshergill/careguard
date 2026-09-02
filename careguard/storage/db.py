from __future__ import annotations

import os
import sqlite3

from careguard.storage.models import SCHEMA
from config.settings import settings


def get_conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(settings.db_path) or ".", exist_ok=True)
    conn = sqlite3.connect(settings.db_path)
    conn.executescript(SCHEMA)
    return conn
