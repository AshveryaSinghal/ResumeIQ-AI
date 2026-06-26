"""
storage.py
SQLite-backed persistence for:
  - users (auth)
  - resume_versions (Resume Version Tracker)
  - analyses (history of ATS runs, used by dashboard + comparisons)

SQLite is used (not a hosted DB) because this is a single-user-per-session
Streamlit app — good enough for Phase 3 without adding infra complexity.
"""

import sqlite3
import json
import time
from contextlib import contextmanager

DB_PATH = "resumeiq.db"


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at REAL NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS resume_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                label TEXT NOT NULL,
                resume_text TEXT NOT NULL,
                filename TEXT,
                created_at REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                resume_version_id INTEGER,
                jd_label TEXT,
                jd_text TEXT,
                overall_score REAL NOT NULL,
                breakdown_json TEXT NOT NULL,
                gap_json TEXT NOT NULL,
                created_at REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (resume_version_id) REFERENCES resume_versions(id)
            )
        """)


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def create_user(username: str, password_hash: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            (username, password_hash, time.time()),
        )


def get_user_by_username(username: str):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        return dict(row) if row else None


# ---------------------------------------------------------------------------
# Resume versions
# ---------------------------------------------------------------------------

def save_resume_version(user_id: int, label: str, resume_text: str, filename: str = None) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO resume_versions (user_id, label, resume_text, filename, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, label, resume_text, filename, time.time()),
        )
        return cur.lastrowid


def get_resume_versions(user_id: int):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM resume_versions WHERE user_id = ? ORDER BY created_at ASC",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Analyses
# ---------------------------------------------------------------------------

def save_analysis(user_id: int, resume_version_id, jd_label: str, jd_text: str,
                   overall_score: float, breakdown: dict, gap: dict) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO analyses (user_id, resume_version_id, jd_label, jd_text, "
            "overall_score, breakdown_json, gap_json, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, resume_version_id, jd_label, jd_text, overall_score,
             json.dumps(breakdown), json.dumps(gap), time.time()),
        )
        return cur.lastrowid


def get_analyses(user_id: int):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT a.*, r.label as resume_label FROM analyses a "
            "LEFT JOIN resume_versions r ON a.resume_version_id = r.id "
            "WHERE a.user_id = ? ORDER BY a.created_at ASC",
            (user_id,),
        ).fetchall()
        results = []
        for r in rows:
            d = dict(r)
            d["breakdown"] = json.loads(d["breakdown_json"])
            d["gap"] = json.loads(d["gap_json"])
            results.append(d)
        return results
