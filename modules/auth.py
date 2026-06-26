"""
auth.py
Minimal username/password authentication using bcrypt for hashing.
Good enough for a personal-project / portfolio-piece login system —
not meant to be production-grade auth (no email verification, password
reset, rate limiting, etc.).
"""

import bcrypt
from . import storage


def signup(username: str, password: str) -> dict:
    username = username.strip().lower()
    if not username or not password:
        return {"success": False, "error": "Username and password are required."}
    if len(password) < 6:
        return {"success": False, "error": "Password must be at least 6 characters."}
    if storage.get_user_by_username(username):
        return {"success": False, "error": "Username already taken."}

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    storage.create_user(username, password_hash)
    user = storage.get_user_by_username(username)
    return {"success": True, "user": user}


def login(username: str, password: str) -> dict:
    username = username.strip().lower()
    user = storage.get_user_by_username(username)
    if not user:
        return {"success": False, "error": "No account with that username."}
    if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return {"success": False, "error": "Incorrect password."}
    return {"success": True, "user": user}
