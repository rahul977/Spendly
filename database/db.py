import os
import sqlite3

from flask import g
from werkzeug.security import generate_password_hash

DATABASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "expense_tracker.db")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            amount      REAL    NOT NULL,
            category    TEXT    NOT NULL,
            date        TEXT    NOT NULL,
            description TEXT,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
    )
    db.commit()


def seed_db():
    db = get_db()

    if db.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
        return

    db.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", generate_password_hash("demo123")),
    )
    db.commit()

    user_id = db.execute("SELECT id FROM users WHERE email = ?", ("demo@spendly.com",)).fetchone()["id"]

    sample_expenses = [
        (user_id, 14.50,  "Food",          "2026-06-02", "Breakfast at bakery"),
        (user_id, 45.00,  "Transport",     "2026-06-05", "Monthly bus pass"),
        (user_id, 120.00, "Bills",         "2026-06-07", "Electricity bill"),
        (user_id, 80.00,  "Health",        "2026-06-10", "Doctor visit"),
        (user_id, 20.00,  "Entertainment", "2026-06-14", "Movie night"),
        (user_id, 65.00,  "Shopping",      "2026-06-18", "New shoes"),
        (user_id, 9.99,   "Other",         "2026-06-22", "Miscellaneous purchase"),
        (user_id, 12.75,  "Food",          "2026-06-28", "Lunch at café"),
    ]
    db.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        sample_expenses,
    )
    db.commit()
