import os
import click
from flask import current_app
from flask.cli import with_appcontext
from app.db import get_db, record_migration, is_migration_applied

@click.group(name='migrations')
def migrations_cli():
    """Команды для управления миграциями."""
    pass

@migrations_cli.command('migrate')
@with_appcontext
def migrate():
    """Применить ожидающие миграции."""
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
                try:
                    with open(migration_path, 'r', encoding='utf-8') as f:
                        migration_sql = f.read()

                    # Execute each statement separately to better handle errors
                    for statement in migration_sql.split(';'):
                        if statement.strip():
                            db.execute(statement)

                    # Commit changes after each migration
                    db.commit()

                    record_migration(db, migration)
                    print(f"Миграция применена: {migration}")

                    # Append the migration SQL to schema.sql
                    with open(schema_path, 'a', encoding='utf-8') as schema_file:
                        schema_file.write(f"\n-- Миграция применена: {migration}\n")
                        schema_file.write(migration_sql)
                        schema_file.write(f"\n \n")
                except Exception as e:
                    print(f"Ошибка при применении миграции {migration}: {str(e)}")
                    db.rollback()
                    raise
        else:
            print("Нет ожидающих миграций.")
    else:
        print("Директория миграций не найдена.")

@migrations_cli.command('status')
@with_appcontext
def status():
    """Показать статус миграций."""
    db = get_db()
    migrations_dir = os.path.join(current_app.root_path, 'migrations')

    if os.path.exists(migrations_dir):
        pending_migrations = []
        applied_migrations = []

        for file in sorted(os.listdir(migrations_dir)):
            if file.endswith('.sql'):
                if is_migration_applied(db, file):
                    applied_migrations.append(file)
                else:
                    pending_migrations.append(file)

        print("\nСтатус миграций:")
        if applied_migrations:
            print("\nПримененные миграции:")
            for migration in applied_migrations:
                print(f"✓ {migration}")

        if pending_migrations:
            print("\nОжидающие миграции:")
            for migration in pending_migrations:
                print(f"✗ {migration}")
            print("\nЧтобы применить эти миграции, выполните:")
            print("flask migrations migrate")

        if not pending_migrations and not applied_migrations:
            print("Миграций не найдено.")
    else:
        print("Директория миграций не найдена.")