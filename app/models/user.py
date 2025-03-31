from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import get_db

class User(UserMixin):
    """Модель для работы с пользователями в базе данных"""
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def set_password(self, password):
        """Установка хэшированного пароля"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Проверка пароля"""
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def create_user(username, password):
        db = get_db()
        if db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone():
            return False
        db.execute(
            'INSERT INTO users (username, password_hash) VALUES (?, ?)',
            (username, generate_password_hash(password))
        )
        db.commit()
        return True

    @staticmethod
    def get_by_username(username):
        """Получение пользователя по имени"""
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()

        if user:
            return User(user['id'], user['username'], user['password_hash'])
        return None

    @staticmethod
    def get_by_id(user_id):
        if not user_id:
            return None
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()
        if user:
            return User(user['id'], user['username'], user['password_hash'])
        return None