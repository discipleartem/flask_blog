import functools
import hashlib
import os
import random

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from app.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


def hash_password(password: str, salt: bytes = None) -> tuple[str, bytes]:
    """Хэширует пароль с использованием SHA-256 и соли."""
    if salt is None:
        salt = os.urandom(16)
    # Используем pbkdf2_hmac для безопасного хэширования
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    # Возвращаем хэш и соль в виде hex-строки для хранения
    return (salt + hashed).hex(), salt


def verify_password(stored_password_hex: str, provided_password: str) -> bool:
    """Проверяет пароль, сравнивая его с сохраненным хэшем."""
    stored_bytes = bytes.fromhex(stored_password_hex)
    salt = stored_bytes[:16]
    stored_hash = stored_bytes[16:]

    new_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
    return new_hash == stored_hash


def generate_discriminator(db, username: str) -> int:
    """Генерирует уникальный дискриминатор для данного username."""
    # Получаем все занятые дискриминаторы для этого username
    existing = db.execute(
        'SELECT discriminator FROM user WHERE username = ?', (username,)
    ).fetchall()

    taken = {row['discriminator'] for row in existing}

    # Пытаемся найти свободный дискриминатор (от 0001 до 9999)
    available = [d for d in range(1, 10000) if d not in taken]

    if not available:
        return None  # Все дискриминаторы заняты для этого username

    return random.choice(available)


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Требуется логин.'
        elif not password:
            error = 'Требуется пароль.'
        elif len(password) < 4:
            error = 'Пароль должен быть не менее 4 символов.'

        if error is None:
            discriminator = generate_discriminator(db, username)

            if discriminator is None:
                error = f'Логин "{username}" полностью занят (все 9999 вариантов).'
            else:
                hashed_password, _ = hash_password(password)
                try:
                    db.execute(
                        'INSERT INTO user (username, discriminator, password) VALUES (?, ?, ?)',
                        (username, discriminator, hashed_password),
                    )
                    db.commit()
                except db.IntegrityError:
                    error = f'Произошла ошибка при регистрации. Попробуйте еще раз.'
                else:
                    flash(f'Регистрация успешна! Ваш логин: {username}#{discriminator:04d}', 'success')
                    return redirect(url_for('auth.login'))

        flash(error, 'danger')

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username_with_tag = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # Парсим username#discriminator
        if '#' in username_with_tag:
            parts = username_with_tag.rsplit('#', 1)
            username = parts[0]
            try:
                discriminator = int(parts[1])
            except ValueError:
                error = 'Неверный формат логина. Используйте: Логин#1234'
                discriminator = None
        else:
            error = 'Неверный формат логина. Используйте: Логин#1234'
            username = None
            discriminator = None

        if error is None:
            user = db.execute(
                'SELECT * FROM user WHERE username = ? AND discriminator = ?',
                (username, discriminator),
            ).fetchone()

            if user is None:
                error = 'Неверный логин или пароль.'
            elif not verify_password(user['password'], password):
                error = 'Неверный логин или пароль.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            flash('Вы успешно вошли!', 'success')
            return redirect(url_for('index'))

        flash(error, 'danger')

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    """Загружает пользователя перед каждым запросом."""
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('index'))


def login_required(view):
    """Декоратор для защиты маршрутов, требующих авторизации."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash('Для этого действия необходимо войти в систему.', 'warning')
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
