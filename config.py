import os
from dotenv import load_dotenv

load_dotenv() # загрузка переменных окружения из файла .env где лежит SECRET_KEY для production


class Config:
    FLASK_APP='app.py'
    DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'blog.db')

    # Отключаем отслеживание изменений в SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(Config):
    ENV = 'production'
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False

    #bash export SECRET_KEY=your_secret_key_value устанавливает переменную окружения SECRET_KEY на сервере
    SECRET_KEY = os.environ.get('SECRET_KEY') # берем SECRET_KEY из переменных окружения
    GITHUB_WEBHOOK_SECRET = os.environ.get('GITHUB_WEBHOOK_SECRET')

    # Enforce HTTPS
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

    # Restrict cookie access
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True

class DevelopmentConfig(Config):
    # Указываем, что это режим разработки
    ENV = 'development'

    # Включаем режим отладки
    DEBUG = True

    # Секретный ключ: проверяем окружение и наличие ключа
    SECRET_KEY = (
        os.environ.get('SECRET_KEY') # берем SECRET_KEY из переменных окружения или указываем значение по умолчанию
        if os.environ.get('ENV') == 'development' and os.environ.get('SECRET_KEY') is not None
        else '239e10887f19b438e7a9b319f435ad6b67137a56696da868d0ec95218035fed481d8f2a83d6e'
    )



