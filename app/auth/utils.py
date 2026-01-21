"""Утилиты для авторизации: хэширование паролей, декораторы."""
import functools
import hashlib
import os
import secrets
from typing import Optional

from flask import flash, g, redirect, url_for

# Константы для настройки безопасности и бизнес-логики
PBKDF2_ITERATIONS = 100000
MAX_DISCRIMINATOR = 9999
SALT_SIZE = 16


def hash_password(password: str, salt: bytes = None) -> tuple[str, bytes]:
    """Хэширует пароль с использованием SHA-256 и соли."""
    if salt is None:
        salt = os.urandom(SALT_SIZE)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, PBKDF2_ITERATIONS)
    # Возвращаем склеенный хэш для хранения и саму соль для БД
    return (salt + hashed).hex(), salt


def verify_password(stored_password: str, provided_password: str, salt: bytes) -> bool:
    """Проверяет пароль, повторно хэшируя его с сохраненной солью."""
    new_hash_hex, _ = hash_password(provided_password, salt)
    return new_hash_hex == stored_password


def generate_discriminator(db_conn, username: str) -> Optional[int]:
    """Генерирует уникальный случайный дискриминатор для данного username."""
    rows = db_conn.execute(
        'SELECT discriminator FROM user WHERE username = ?', (username,)
    ).fetchall()

    taken_discriminators = {row['discriminator'] for row in rows}
    all_possible = set(range(1, MAX_DISCRIMINATOR + 1))
    available = list(all_possible - taken_discriminators)

    if not available:
        return None

    return secrets.choice(available)


def login_required(view):
    """Декоратор для защиты маршрутов, требующих авторизации."""

    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            flash('Для этого действия необходимо войти в систему.', 'warning')
            return redirect(url_for('auth.login'))
        return view(*args, **kwargs)

    return wrapped_view
