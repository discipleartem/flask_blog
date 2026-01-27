"""Модуль для работы с базой данных SQLite.

Идея:
- одно соединение на один запрос (хранится в flask.g),
- автоматическое закрытие соединения через teardown,
- команда CLI `flask init-db` для инициализации схемы.
"""

import sqlite3  # работа с SQLite
import warnings  # подавление предупреждений
from typing import Any

import click
from flask import Flask, g, current_app
from sqlite3 import Connection

# Подавляем предупреждение об устаревшем конвертере временных меток Python
# 3.12+
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    module="sqlite3",
    message=".*default timestamp converter.*",
)


def get_db() -> Connection:
    """Возвращает соединение с БД для текущего контекста запроса.

    Если соединение ещё не создано — создаёт, настраивает row_factory и кладёт в g.db.

    Почему так:
    - g живёт ровно в рамках одного запроса,
    - мы избегаем глобального соединения и проблем с потоками/контекстами.
    """
    if "db" not in g:
        # Создаём соединение с БД из конфигурации приложения
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        # Позволяет обращаться к колонкам по именам, как к словарю
        g.db.row_factory = sqlite3.Row

    return g.db  # type: ignore


def close_db(e: Any = None) -> None:
    """Закрывает соединение с БД, если оно было открыто.

    Вызывается автоматически при завершении обработки запроса (teardown_appcontext).
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    """Инициализирует БД: создаёт таблицы из SQL-скрипта schema.sql."""
    db = get_db()
    # current_app.open_resource ищет файл относительно пакета приложения
    with current_app.open_resource("db/schema.sql") as f:
        schema_sql = f.read().decode("utf-8")
        db.executescript(schema_sql)


@click.command("init-db")
def init_db_command() -> None:
    """CLI-команда: очистить/создать таблицы (запускается как `flask init-db`)."""
    init_db()
    click.echo("База данных инициализирована.")


def init_app(app: Flask) -> None:
    """Подключает БД к Flask-приложению.

    - регистрирует закрытие соединения на teardown,
    - добавляет CLI-команду init-db.

    Args:
        app: экземпляр Flask-приложения.
    """
    # Указываем Flask закрывать соединение с БД при очистке контекста
    # приложения
    app.teardown_appcontext(close_db)
    # Добавляем команду в CLI flask
    app.cli.add_command(init_db_command)
