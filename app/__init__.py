from flask import Flask
from flask_login import LoginManager
import sqlite3
import os
from .db import close_db, init_db, DATABASE

# Создание экземпляра приложения Flask
app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig') # Загрузка конфигурации из файла config.py

# Инициализация менеджера авторизации
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

app.teardown_appcontext(close_db)

# Создание базы данных, если она не существует
if not os.path.exists(DATABASE):
    with app.app_context():
        init_db()

# Импорт маршрутов из blueprints (по сути, это отдельные модули)
from app.routes.auth_routes import bp as auth_routes
from app.routes.article_routes import bp as article_routes
from app.routes.сomment_routes import bp as comment_routes

# Регистрация blueprints
app.register_blueprint(auth_routes)
app.register_blueprint(article_routes)
app.register_blueprint(comment_routes)