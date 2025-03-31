import sqlite3
import click
from flask import g, current_app
from flask.cli import with_appcontext

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

def close_db(e=None):
    """Закрытие соединения с базой данных"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Инициализация базы данных"""
    db = get_db()
    with current_app.open_resource('../schema.sql') as f:
        db.executescript(f.read().decode('utf8'))



""" click
Предоставляет CLI-интерфейс для Flask приложения
Позволяет создавать команды для управления приложением из командной строки
В данном случае создает команду flask init-db для инициализации базы данных
Удобно для первоначальной настройки приложения и управления БД"""

""" @with_appcontext
Декоратор, который гарантирует, что команда будет выполняться в контексте приложения
Обеспечивает доступ к current_app и другим контекстно-зависимым объектам
Необходим для корректной работы с БД через CLI-команды
Без него команда flask init-db не сможет получить доступ к контексту приложения"""

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    """Register database functions with the Flask app"""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)