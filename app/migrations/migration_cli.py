import os
import click
from flask import current_app
from flask.cli import with_appcontext
from app.db import get_db, record_migration

@click.group()
def migrations_cli():
    """Migration commands."""
    pass

@migrations_cli.command('migrate')
@with_appcontext
def migrate():
    """Apply pending migrations."""
    db = get_db()
    migrations_dir = os.path.join(current_app.root_path, 'migrations')
    schema_path = os.path.join(os.path.dirname(current_app.root_path), 'schema.sql')

    if os.path.exists(migrations_dir):
        pending_migrations = []
        for file in sorted(os.listdir(migrations_dir)):
            if file.endswith('.sql') and not is_migration_applied(db, file):
                pending_migrations.append(file)

        if pending_migrations:
            for migration in pending_migrations:
                migration_path = os.path.join(migrations_dir, migration)
                with open(migration_path, 'r', encoding='utf-8') as f:
                    migration_sql = f.read()
                    db.executescript(migration_sql)
                record_migration(db, migration)
                print(f"Applied migration: {migration}")

                # Append the migration SQL to schema.sql
                with open(schema_path, 'a', encoding='utf-8') as schema_file:
                    schema_file.write(f"\n-- Applied migration: {migration}\n")
                    schema_file.write(migration_sql)
        else:
            print("No pending migrations found.")
    else:
        print("Migrations directory not found.")

def is_migration_applied(db, filename):
    """Check if a migration has been applied."""
    result = db.execute("""
        SELECT 1 FROM migrations WHERE filename = ?
    """, (filename,)).fetchone()
    return result is not None