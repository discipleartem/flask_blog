"""Модуль работы с базой данных."""

from app.db.db import close_db, get_db, init_app, init_db

__all__ = ['get_db', 'close_db', 'init_db', 'init_app']
