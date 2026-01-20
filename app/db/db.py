"""Модуль для работы с базой данных SQLite."""

import sqlite3

import click
from flask import current_app, g


def get_db():
    """Получает соединение с базой данных для текущего контекста запроса.
    
    Если соединение ещё не создано, создаёт новое и сохраняет в g.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # Позволяет обращаться к колонкам по именам, как к словарю
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(_=None):
    """Закрывает соединение с базой данных, если оно было открыто."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    # Путь должен быть обновлен на app/db/schema.sql
    with current_app.open_resource('db/schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """Очистить существующие данные и создать новые таблицы."""
    init_db()
    click.echo('База данных инициализирована.')


def init_app(app):
    """Регистрирует функции работы с БД в приложении Flask.
    
    Args:
        app: Экземпляр Flask-приложения
    """
    # Указываем Flask закрывать соединение с БД при очистке контекста приложения
    app.teardown_appcontext(close_db)
    # Добавляем команду в CLI flask
    app.cli.add_command(init_db_command)
