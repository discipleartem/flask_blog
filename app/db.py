import datetime
import os
import sqlite3
from flask import g, current_app

DATABASE = 'blog.db'

def get_db():
    """Соединение с базой данных"""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config.get('DATABASE', DATABASE)
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(_=None):
    """Закрытие соединения с базой данных"""
    db = g.pop('db', None)
    if db is not None:
        db.close()



def check_table_exists(db, table_name):
    """Check if a table exists in the database"""
    return db.execute("""
        SELECT 1 FROM sqlite_master
        WHERE type='table' AND name=?
    """, (table_name,)).fetchone() is not None


def check_column_exists(db, table_name, column_name):
    """Check if a column exists in the table"""
    try:
        db.execute(f"SELECT {column_name} FROM {table_name} LIMIT 0")
        return True
    except sqlite3.OperationalError:
        return False


def init_db():
    """Initialize database if it doesn't exist"""
    db = get_db()
    try:
        # Check if any tables exist (excluding system tables)
        tables = db.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table'
            AND name NOT IN ('sqlite_sequence')
        """).fetchall()

        if not tables:
            # Initialize new database from schema
            schema_path = os.path.join(os.path.dirname(current_app.root_path), 'schema.sql')
            with open(schema_path, 'r', encoding='utf-8') as f:
                db.executescript(f.read())
            db.commit()
            print("Database initialized from schema")

        # Check for pending migrations
        migrations_dir = os.path.join(current_app.root_path, 'migrations')
        if os.path.exists(migrations_dir):
            pending_migrations = []
            for file in sorted(os.listdir(migrations_dir)):
                if file.endswith('.sql') and not is_migration_applied(db, file):
                    pending_migrations.append(file)

            if pending_migrations:
                print("\nPending migrations found:")
                for migration in pending_migrations:
                    print(f"- {migration}")
                print("\nTo apply migrations, run:")
                print("flask migrations-cli migrate")

    except sqlite3.Error as e:
        db.rollback()
        raise Exception(f"Database initialization failed: {e}")


def is_migration_applied(db, filename):
    """Check if a migration has been applied"""
    result = db.execute("""
        SELECT 1 FROM migrations WHERE filename = ?
    """, (filename,)).fetchone()
    return result is not None

def record_migration(db, filename):
    """Record a migration as applied"""
    db.execute("""
        INSERT INTO migrations (filename, applied_at) VALUES (?, ?)
    """, (filename, datetime.datetime.now()))
    db.commit()