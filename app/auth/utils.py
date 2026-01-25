"""Утилиты для авторизации: хэширование паролей, декораторы."""

import functools
import secrets
from typing import Optional

from flask import flash, g, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash

# Максимальное значение тега (дискриминатора), как в Discord (от 0001 до 9999).
MAX_DISCRIMINATOR = 9999


def hash_password(password: str, salt: bytes = None) -> tuple[str, bytes]:
    """Хэширует пароль с использованием werkzeug.security.

    Args:
        password: Пароль для хэширования
        salt: Опциональная соль (16 байт). Если не предоставлена, генерируется случайно.

    Returns:
        tuple[str, bytes]: (хэш пароля, соль)
    """
    if salt is None:
        # Генерируем случайную соль
        salt = secrets.token_bytes(16)

    # Конвертируем соль в hex для хранения в хэше
    salt_hex = salt.hex()

    # Используем PBKDF2 хэширование с нашей солью
    import hashlib

    # PBKDF2 хэширование
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    hashed_hex = hashed.hex()

    return f"pbkdf2_sha256${salt_hex}${hashed_hex}", salt


def verify_password(stored_password: str, provided_password: str, salt: bytes) -> bool:
    """Проверяет пароль.

    Args:
        stored_password: Хэш из базы данных
        provided_password: Предоставленный пароль
        salt: Соль, которая использовалась при хэшировании

    Returns:
        bool: True если пароль верный
    """
    try:
        import hashlib
        import hmac

        # Разбираем сохраненный хэш
        parts = stored_password.split("$")
        if len(parts) != 3 or parts[0] != "pbkdf2_sha256":
            return False

        stored_salt_hex = parts[1]
        stored_hash_hex = parts[2]

        # Проверяем, что соль в хэше совпадает с переданной
        if salt.hex() != stored_salt_hex:
            return False

        # Вычисляем хэш с той же солью
        hashed = hashlib.pbkdf2_hmac("sha256", provided_password.encode(), salt, 100000)
        computed_hash_hex = hashed.hex()

        # Сравниваем хэши
        return hmac.compare_digest(computed_hash_hex, stored_hash_hex)
    except Exception:
        return False


def generate_discriminator(db_conn, username: str) -> Optional[int]:
    """
    Генерирует уникальный случайный дискриминатор (тег) для пользователя.

    Позволяет существовать нескольким пользователям с одинаковым именем,
    но разными тегами (например, User#0001 и User#0002).
    """
    # Получаем список всех занятых тегов для данного имени пользователя
    rows = db_conn.execute(
        "SELECT discriminator FROM user WHERE username = ?", (username,)
    ).fetchall()

    taken_discriminators = {row["discriminator"] for row in rows}

    # Создаем множество всех возможных тегов (от 1 до 9999)
    all_possible = set(range(1, MAX_DISCRIMINATOR + 1))
    # Определяем, какие теги еще свободны
    available = list(all_possible - taken_discriminators)

    if not available:
        # Если все 9999 комбинаций заняты для этого имени
        return None

    # Выбираем случайный свободный тег
    return secrets.choice(available)


def login_required(view):
    """Декоратор для защиты маршрутов."""

    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            flash("Для этого действия необходимо войти в систему.", "warning")
            return redirect(url_for("auth.login"))

        return view(*args, **kwargs)

    return wrapped_view
