"""Утилиты для авторизации: хэширование паролей, декораторы."""

import functools
import hashlib
import os
import secrets
from typing import Optional

from flask import flash, g, redirect, url_for


def hash_password(password: str, salt: bytes = None) -> tuple[str, bytes]:
    """Хэширует пароль с использованием SHA-256 и соли."""
    if salt is None:
        salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return (salt + hashed).hex(), salt


def verify_password(stored_password_hex: str, provided_password: str) -> bool:
    """Проверяет пароль, сравнивая его с сохраненным хэшем."""
    stored_bytes = bytes.fromhex(stored_password_hex)
    salt = stored_bytes[:16]
    stored_hash = stored_bytes[16:]
    new_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
    return new_hash == stored_hash


def generate_discriminator(db, username: str) -> Optional[int]:
    """Генерирует уникальный дискриминатор для данного username."""
    existing = db.execute(
        'SELECT discriminator FROM user WHERE username = ?', (username,)
    ).fetchall()

    taken = {row['discriminator'] for row in existing}
    available = [d for d in range(1, 10000) if d not in taken]

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
