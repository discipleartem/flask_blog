import sqlite3

import click
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # Позволяет обращаться к колонкам по именам, как к словарю
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    # current_app.open_resource открывает файл относительно пакета app
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """Очистить существующие данные и создать новые таблицы."""
    init_db()
    click.echo('База данных инициализирована.')


def init_app(app):
    # Указываем Flask закрывать соединение с БД при очистке контекста приложения
    app.teardown_appcontext(close_db)
    # Добавляем команду в CLI flask
    app.cli.add_command(init_db_command)
