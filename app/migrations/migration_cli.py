# app/migrations/migration_cli.py
import click
import os
from flask import current_app
from flask.cli import with_appcontext
from ..db import get_db, check_column_exists

@click.group()
def migrations_cli():
    """Database migration commands."""
    pass

@migrations_cli.command('migrate')
@with_appcontext
def migrate_command():
    """Apply database migrations"""
    db = get_db()
    migrations_dir = os.path.join(current_app.root_path, 'migrations')

    db.execute("""
        CREATE TABLE IF NOT EXISTS migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()

    for migration_file in sorted(os.listdir(migrations_dir)):
        if not migration_file.endswith('.sql'):
            continue

        if db.execute('SELECT 1 FROM migrations WHERE name = ?', (migration_file,)).fetchone():
            continue

        with open(os.path.join(migrations_dir, migration_file), 'r') as f:
            migration_sql = f.read()

            if 'articles' in migration_file and 'updated_at' in migration_sql:
                if check_column_exists(db, 'articles', 'updated_at'):
                    print(f"Skipping {migration_file}: column already exists")
                    continue

        try:
            db.executescript(migration_sql)
            db.execute('INSERT INTO migrations (name) VALUES (?)', (migration_file,))
            db.commit()
            print(f"Applied: {migration_file}")

            # Update schema.sql file
            schema_path = os.path.join(current_app.root_path, '..', 'schema.sql')
            with open(schema_path, 'a', encoding='utf-8') as schema_file:
                schema_file.write(f"\n-- Applied migration: {migration_file}\n")
                schema_file.write(migration_sql)
                print(f"Updated schema.sql with {migration_file}")

        except Exception as e:
            db.rollback()
            print(f"Failed to apply {migration_file}: {e}")