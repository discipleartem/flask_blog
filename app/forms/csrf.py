import hashlib
import hmac
import os

from flask import session, current_app


def generate_csrf_token():
    """Генерирует CSRF-токен, привязанный к сессии.

    Реализация:
    - в session хранится случайная "основа" (_csrf_token),
    - клиенту выдаём HMAC-SHA256 подпись этой основы с SECRET_KEY,
      чтобы токен нельзя было сгенерировать вне сервера.

    Returns:
        str: подписанный CSRF-токен (hex).
    """
    if '_csrf_token' not in session:
        # Случайное значение на сессию
        session['_csrf_token'] = os.urandom(32).hex()

    # Создаем подпись токена, чтобы его нельзя было подделать вне сервера
    key = current_app.config['SECRET_KEY'].encode()
    token = session['_csrf_token'].encode()
    return hmac.new(key, token, hashlib.sha256).hexdigest()


def validate_csrf_token(token):
    """Проверяет CSRF-токен на совпадение с ожидаемым.

    Args:
        token: строка токена из формы.

    Returns:
        bool: True если токен валиден.
    """
    if not token or '_csrf_token' not in session:
        return False

    expected_token = generate_csrf_token()
    # compare_digest защищает от тайминговых атак
    return hmac.compare_digest(expected_token, token)
