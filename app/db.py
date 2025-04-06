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
        # Проверяем, есть ли вообще какие-либо таблицы в БД
        tables = db.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table'
            AND name NOT IN ('sqlite_sequence')
        """).fetchall()

        is_new_db = len(tables) == 0

        if is_new_db:
            # Инициализируем новую базу данных из схемы
            schema_path = os.path.join(os.path.dirname(current_app.root_path), 'schema.sql')
            with open(schema_path, 'r', encoding='utf-8') as f:
                db.executescript(f.read())
            db.commit()
            print("База данных инициализирована из схемы")

        # Только если таблица migrations еще не существует, создаем ее
        # Это позволяет создать migrations при первом запуске и избежать ошибок,
        # если таблицы нет (например, при переносе БД из старой версии приложения)
        if not check_table_exists(db, 'migrations'):
            db.execute("""
                CREATE TABLE migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            db.commit()
            print("Создана таблица для отслеживания миграций")

        # Проверяем наличие ожидающих миграций
        migrations_dir = os.path.join(current_app.root_path, 'migrations')
        if os.path.exists(migrations_dir):
            pending_migrations = []
            for file in sorted(os.listdir(migrations_dir)):
                if file.endswith('.sql') and not is_migration_applied(db, file):
                    pending_migrations.append(file)

            if pending_migrations:
                print("\nНайдены ожидающие миграции:")
                for migration in pending_migrations:
                    print(f"- {migration}")
                print("\nЧтобы применить миграции, выполните:")
                print("flask migrations migrate")

    except sqlite3.Error as e:
        db.rollback()
        print(f"Ошибка инициализации базы данных: {e}")
        # Не останавливаем приложение при ошибке
        # raise Exception(f"Database initialization failed: {e}")

def is_migration_applied(db, filename):
    """Check if a migration has been applied"""
    # Таблица migrations должна существовать
    if not check_table_exists(db, 'migrations'):
        return False

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