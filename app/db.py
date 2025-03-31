import os
import sqlite3
from flask import g, current_app

DATABASE = 'blog.db'

""" current_app
Это прокси-объект Flask, который указывает на текущее активное приложение
Позволяет безопасно получать доступ к конфигурации приложения из любого места кода
Особенно важен при тестировании, где мы используем разные конфигурации для тестовой и боевой базы данных
В вашем коде это нужно для current_app.config.get('DATABASE', DATABASE), чтобы использовать тестовую БД из конфигурации при тестах"""

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

def init_db():
    """Initialize database and tables if they don't exist"""
    db = get_db()
    try:
        # Check if database file exists
        db_path = current_app.config.get('DATABASE', DATABASE)
        db_exists = os.path.exists(db_path)

        if not db_exists:
            # Create database file
            db.commit()

        # Check if required tables exist
        required_tables = ['users', 'articles', 'comments']
        existing_tables = db.execute("""
            SELECT name FROM sqlite_master WHERE type='table'
        """).fetchall()
        existing_tables = [table['name'] for table in existing_tables]

        # Create only missing tables
        if not all(table in existing_tables for table in required_tables):
            schema_path = os.path.join(os.path.dirname(current_app.root_path), 'schema.sql')
            with open(schema_path, 'r', encoding='utf-8') as f:
                db.executescript(f.read())
            db.commit()
            print("Database tables initialized.")
        else:
            print("Database and tables already exist.")

    except sqlite3.Error as e:
        db.rollback()
        raise Exception(f"Database initialization failed: {e}")
    except IOError as e:
        raise Exception(f"Could not read schema file: {e}")
