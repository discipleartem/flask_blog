"""Утилиты для авторизации: хэширование паролей, декораторы."""
import functools
import hashlib
import os
import secrets
from typing import Optional

from flask import flash, g, redirect, url_for

# Константы для настройки безопасности и бизнес-логики
# Количество итераций для PBKDF2. Чем больше, тем сложнее перебор пароля.
PBKDF2_ITERATIONS = 100000
# Максимальное значение тега (дискриминатора), как в Discord (от 0001 до 9999).
MAX_DISCRIMINATOR = 9999
# Размер соли в байтах для обеспечения уникальности хэша даже при одинаковых паролях.
SALT_SIZE = 16


def hash_password(password: str, salt: bytes = None) -> tuple[str, bytes]:
    """
    Хэширует пароль с использованием PBKDF2-HMAC-SHA256.
    
    Если соль не передана, генерирует новую случайную соль.
    Возвращает кортеж: (склеенный_хэш_в_hex, соль).
    """
    if salt is None:
        # Генерируем случайную соль, если это регистрация нового пользователя
        salt = os.urandom(SALT_SIZE)

    # Применяем алгоритм PBKDF2 для безопасного хэширования
    hashed = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        PBKDF2_ITERATIONS
    )

    # Для удобства хранения возвращаем соль + хэш в виде одной hex-строки
    # и саму соль отдельно для сохранения в БД.
    return (salt + hashed).hex(), salt


def verify_password(stored_password: str, provided_password: str, salt: bytes) -> bool:
    """Проверяет пароль, повторно хэшируя его с сохраненной солью."""
    new_hash_hex, _ = hash_password(provided_password, salt)
    return new_hash_hex == stored_password


def generate_discriminator(db_conn, username: str) -> Optional[int]:
    """
    Генерирует уникальный случайный дискриминатор (тег) для пользователя.
    
    Позволяет существовать нескольким пользователям с одинаковым именем,
    но разными тегами (например, User#0001 и User#0002).
    """
    # Получаем список всех занятых тегов для данного имени пользователя
    rows = db_conn.execute(
        'SELECT discriminator FROM user WHERE username = ?', (username,)
    ).fetchall()

    taken_discriminators = {row['discriminator'] for row in rows}
    # Создаем множество всех возможных тегов (от 1 до 9999)
    all_possible = set(range(1, MAX_DISCRIMINATOR + 1))
    # Определяем, какие теги еще свободны
    available = list(all_possible - taken_discriminators)

    if not available:
        # Если все 9999 комбинаций заняты для этого имени
        return None

    # Выбираем случайный свободный тег для криптографической стойкости
    return secrets.choice(available)


def login_required(view):
    """
    Декоратор для защиты маршрутов (view functions).
    
    Если пользователь не авторизован (отсутствует в объекте g.user),
    перенаправляет его на страницу входа с уведомлением.
    """
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            # Если в глобальном объекте Flask нет данных о пользователе
            flash('Для этого действия необходимо войти в систему.', 'warning')
            return redirect(url_for('auth.login'))

        # Выполняем основную функцию, если проверка пройдена
        return view(*args, **kwargs)

    return wrapped_view
