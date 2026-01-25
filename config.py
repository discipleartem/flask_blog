import os


class Config:
    # Секретный ключ для сессий и защиты форм
    # SECRET_KEY переменная из .env файла
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE = os.path.join(BASE_DIR, "instance", "flask_blog.sqlite")

    # Пароль для admin пользователя
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    DATABASE = ":memory:"  # SQLite в памяти для тестов
    WTF_CSRF_ENABLED = True  # Включаем CSRF для тестов
