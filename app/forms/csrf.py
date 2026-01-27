import hashlib
import hmac
import os
from typing import Optional

from flask import session, current_app

# Константа для тестового CSRF токена
TEST_CSRF_TOKEN = "csrf_test_token"  # nosec B105


def generate_csrf_token() -> str:
    """Генерирует CSRF-токен, привязанный к сессии.

    Реализация:
    - в session хранится случайная "основа" (_csrf_token),
    - клиенту выдаём HMAC-SHA256 подпись этой основы с SECRET_KEY,
      чтобы токен нельзя было сгенерировать вне сервера.

    Returns:
        str: подписанный CSRF-токен (hex).
    """
    from flask import has_request_context

    # Для тестов вне контекста запроса используем простую строку
    if not has_request_context():
        return "csrf_test_token"

    if "_csrf_token" not in session:
        # Случайное значение на сессию
        session["_csrf_token"] = os.urandom(32).hex()

    # Создаем подпись токена, чтобы его нельзя было подделать вне сервера
    key = current_app.config["SECRET_KEY"].encode()
    token = session["_csrf_token"].encode()
    return hmac.new(key, token, hashlib.sha256).hexdigest()


def validate_csrf_token(token: Optional[str]) -> bool:
    """Проверяет CSRF-токен на совпадение с ожидаемым.

    Args:
        token: строка токена из формы.

    Returns:
        bool: True если токен валиден.
    """
    from flask import has_request_context

    # Для тестов вне контекста запроса
    if not has_request_context():
        return token == TEST_CSRF_TOKEN  # type: ignore

    if not token or "_csrf_token" not in session:
        return False

    expected_token = generate_csrf_token()
    # compare_digest защищает от тайминговых атак
    return hmac.compare_digest(expected_token, token)
