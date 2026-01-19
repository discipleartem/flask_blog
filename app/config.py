import os


class Config:
    # Секретный ключ для сессий и защиты форм
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # Путь к базе данных SQLite (на уровень выше, в папку instance)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE = os.path.join(os.path.dirname(BASE_DIR), 'instance', 'flask_blog.sqlite')
