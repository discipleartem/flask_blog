"""SQLite helpers and custom migrations."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from flask import Flask, current_app, g
from werkzeug.security import generate_password_hash


def get_db() -> sqlite3.Connection:
    """Return a request-scoped SQLite connection."""
    if "db" not in g:
        path = current_app.config["DATABASE"]
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        g.db = conn
    return g.db


def close_db(_: BaseException | None = None) -> None:
    """Close the request-scoped connection."""
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def query_all(sql: str, args: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
    """Run SELECT and return all rows."""
    return get_db().execute(sql, args).fetchall()


def query_one(sql: str, args: tuple[Any, ...] = ()) -> sqlite3.Row | None:
    """Run SELECT and return one row or None."""
    return get_db().execute(sql, args).fetchone()


def execute(sql: str, args: tuple[Any, ...] = ()) -> int:
    """Run INSERT/UPDATE/DELETE and return lastrowid."""
    db = get_db()
    cur = db.execute(sql, args)
    db.commit()
    return int(cur.lastrowid)


def execute_script(sql: str) -> None:
    """Execute a multi-statement SQL script."""
    db = get_db()
    db.executescript(sql)
    db.commit()


def _ensure_migrations_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL UNIQUE,
            applied_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    conn.commit()


def run_migrations(app: Flask | None = None) -> list[str]:
    """Apply pending SQL files from migrations/ in sorted order."""
    ctx_app = app or current_app
    migrations_dir: Path = ctx_app.config["MIGRATIONS_DIR"]
    applied: list[str] = []

    with ctx_app.app_context():
        db = get_db()
        _ensure_migrations_table(db)
        done = {
            row["filename"]
            for row in db.execute("SELECT filename FROM schema_migrations").fetchall()
        }
        files = sorted(migrations_dir.glob("*.sql"))
        for path in files:
            if path.name in done:
                continue
            sql = path.read_text(encoding="utf-8")
            db.executescript(sql)
            db.execute(
                "INSERT INTO schema_migrations (filename) VALUES (?)",
                (path.name,),
            )
            db.commit()
            applied.append(path.name)
    return applied


def seed_admin(app: Flask | None = None) -> bool:
    """Ensure a single admin#0001 user exists. Returns True if created."""
    ctx_app = app or current_app
    with ctx_app.app_context():
        existing = query_one(
            "SELECT id FROM users WHERE name = ? AND discriminator = ?",
            ("admin", "0001"),
        )
        if existing is not None:
            return False
        password = ctx_app.config["ADMIN_PASSWORD"]
        execute(
            """
            INSERT INTO users (name, discriminator, password_hash, is_admin)
            VALUES (?, ?, ?, 1)
            """,
            ("admin", "0001", generate_password_hash(password)),
        )
        return True


def init_db(app: Flask | None = None) -> None:
    """Run migrations and seed admin."""
    run_migrations(app)
    seed_admin(app)


def init_app(app: Flask) -> None:
    """Register DB teardown and CLI."""
    app.teardown_appcontext(close_db)

    @app.cli.command("db-upgrade")
    def db_upgrade_command() -> None:
        """Apply pending migrations and seed admin."""
        applied = run_migrations(app)
        created = seed_admin(app)
        if applied:
            print(f"Applied: {', '.join(applied)}")
        else:
            print("No pending migrations.")
        print("Admin seeded." if created else "Admin already present.")
