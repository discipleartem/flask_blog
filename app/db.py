import sqlite3
from flask import g

DATABASE = 'blog.db'

def get_db():
    """Соединение с базой данных"""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Закрытие соединения с базой данных"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Инициализация базы данных"""
    db = get_db()
    with open('schema.sql', 'r') as f:
        db.executescript(f.read())