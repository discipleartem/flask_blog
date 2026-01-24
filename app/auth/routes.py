"""Маршруты авторизации.

Содержит:
- регистрацию пользователя (с генерацией дискриминатора),
- вход по формату username#0001,
- загрузку пользователя в g.user для каждого запроса,
- выход (logout).
"""

import sqlite3

from flask import flash, g, redirect, render_template, request, session, url_for, current_app, make_response

from app.auth import bp
from app.auth.utils import generate_discriminator, hash_password, verify_password
from app.db import get_db
from app.forms import RegistrationForm, LoginForm

# Константы для cookie
COOKIE_DAYS = 30
COOKIE_OPTIONS = {
    'max_age': COOKIE_DAYS * 24 * 60 * 60,
    'httponly': True,
    'secure': True,
    'samesite': 'Strict'
}


def set_auth_cookie(response, username):
    """Устанавливает HttpOnly cookie с логином пользователя."""
    response.set_cookie('last_username', username, **COOKIE_OPTIONS)


def create_user_session(user_id):
    """Создаёт сессию для пользователя."""
    session.clear()
    session['user_id'] = user_id
    session.permanent = True


def format_full_username(username, discriminator):
    """Форматирует полный логин с дискриминатором."""
    return f"{username}#{discriminator:04d}" if discriminator > 0 else username


def get_prefilled_usernames():
    """Возвращает полный и базовый логины из cookie для автозаполнения.
    
    Фикс логина с дискриминатором:
    - prefilled_username: полный логин (user#1234) для скрытого поля
    - prefilled_base_username: базовый логин (user) для видимого поля
    Это позволяет браузеру корректно автозаполнять пароль.
    """
    prefilled_username = request.cookies.get('last_username', '')
    prefilled_base_username = prefilled_username.split('#')[0] if prefilled_username else ''
    return prefilled_username, prefilled_base_username


def authenticate_admin(password):
    """Аутентифицирует admin пользователя."""
    if password != current_app.config['ADMIN_PASSWORD']:
        return None, 'Неверный пароль для admin'
    
    db = get_db()
    admin_user = db.execute(
        'SELECT * FROM user WHERE username = ?', ('admin',)
    ).fetchone()
    
    if admin_user is None:
        hashed_pw, salt = hash_password(password)
        db.execute(
            "INSERT INTO user (username, password, discriminator, salt) VALUES (?, ?, ?, ?)",
            ('admin', hashed_pw, 0, salt),
        )
        db.commit()
        admin_user = db.execute(
            'SELECT * FROM user WHERE username = ?', ('admin',)
        ).fetchone()
    
    return admin_user, None


def authenticate_user(username_to_check, password):
    """Аутентифицирует обычного пользователя по логину с дискриминатором."""
    if "#" not in username_to_check:
        return None, 'Неверный формат логина'
    
    try:
        username, tag_str = username_to_check.rsplit("#", 1)
        tag = int(tag_str)
    except (ValueError, IndexError):
        return None, 'Неверный формат логина'
    
    db = get_db()
    user = db.execute(
        'SELECT * FROM user WHERE username = ? AND discriminator = ?',
        (username, tag)
    ).fetchone()
    
    if user is None:
        return None, 'Неверный логин или пароль'
    
    if not verify_password(user['password'], password, user['salt']):
        return None, 'Неверный логин или пароль'
    
    return user, None


@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Регистрация нового пользователя.

    Валидация:
    - username обязателен и не содержит '#'
    - пароль минимум 4 символа
    - имя 'admin' зарезервировано

    При успехе создаём запись в таблице user и предлагаем войти.
    """
    form = RegistrationForm(request.form)
    
    if request.method == 'POST' and form.validate():
        password = form.password.data
        db = get_db()
        error = None

        username = form.username.data.strip()
        if username.lower() == 'admin':
            error = 'Имя admin зарезервировано системой'
        else:
            # Генерация уникального дискриминатора (1..9999) для одинаковых username
            new_tag = generate_discriminator(db, username)

            if new_tag is None:
                error = f"К сожалению, имя {username} перегружено. Попробуйте другое."
            else:
                full_username = format_full_username(username, new_tag)
                tag = new_tag

        if error is None:
            try:
                # Пароль храним только в виде хэша с солью
                hashed_pw, salt = hash_password(password)
                cursor = db.execute(
                    "INSERT INTO user (username, password, discriminator, salt) VALUES (?, ?, ?, ?)",
                    (username, hashed_pw, tag, salt),
                )
                db.commit()
                
                # Получаем ID созданного пользователя для автоматического входа
                user_id = cursor.lastrowid
                
                # Устанавливаем сессию для автоматического входа
                create_user_session(user_id)
                
                # ФИКС ЛОГИНА С ДИСКРИМИНАТОРОМ: сохраняем полный логин в HttpOnly cookie
                # Это позволяет подставлять полный логин при следующем входе
                response = make_response(redirect(url_for("main.index")))
                set_auth_cookie(response, full_username)
                
                flash(f'Добро пожаловать {full_username}!', 'success')
                return response
            except sqlite3.IntegrityError:
                error = "Ошибка при регистрации. Возможно, имя занято."

        if error:
            flash(error, 'danger')
    
    # Если форма не валидна, показываем ошибки формы
    elif request.method == 'POST':
        for field_name, field_errors in form.errors.items():
            for error in field_errors:
                flash(error, 'danger')

    return render_template('auth/register.html', form=form)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Вход пользователя.

    Ожидаемый формат логина: Username#0001
    (где 0001 — discriminator, хранимый в БД как число).
    
    Особый случай: admin может входить без дискриминатора.
    """
    # Получаем username из cookie для автозаполнения
    prefilled_username, prefilled_base_username = get_prefilled_usernames()
    
    form = LoginForm(request.form)
    
    if request.method == 'POST' and form.validate():
        raw_username = request.form.get('username', '').strip()
        full_username_hidden = request.form.get('full_username', '').strip()
        password = request.form.get('password', '')
        db = get_db()
        error = None

        # ФИКС ЛОГИНА С ДИСКРИМИНАТОРОМ: приоритет скрытого поля с полным логином
        # Если есть скрытое поле с полным логином (user#1234), используем его
        # Иначе используем то, что ввёл пользователь в видимое поле
        username_to_check = full_username_hidden if full_username_hidden and '#' in full_username_hidden else raw_username

        # Особый случай для admin: вход без дискриминатора
        if username_to_check.lower() == 'admin':
            admin_user, error = authenticate_admin(password)
            if admin_user:
                create_user_session(admin_user['id'])
                # ФИКС ЛОГИНА С ДИСКРИМИНАТОРОМ: сохраняем полный логин в HttpOnly cookie
                response = make_response(redirect(url_for('main.index')))
                set_auth_cookie(response, 'admin')
                flash('Добро пожаловать, admin!', 'success')
                return response
        
        # Фикс логина с дискриминатором: ожидаем формат username#0001 и ищем пару (username, discriminator)
        else:
            user, error = authenticate_user(username_to_check, password)
            if user:
                create_user_session(user['id'])
                full_username = format_full_username(user['username'], user['discriminator'])
                # ФИКС ЛОГИНА С ДИСКРИМИНАТОРОМ: сохраняем полный логин в HttpOnly cookie
                response = make_response(redirect(url_for('main.index')))
                set_auth_cookie(response, full_username)
                return response

        flash(error, 'danger')
    
    # Если форма не валидна, показываем ошибки формы
    elif request.method == 'POST':
        for field_name, field_errors in form.errors.items():
            for error in field_errors:
                flash(error, 'danger')

    return render_template('auth/login.html', form=form, prefilled_username=prefilled_username, prefilled_base_username=prefilled_base_username)


@bp.before_app_request
def load_logged_in_user():
    """Загружает текущего пользователя в g.user перед обработкой любого запроса.

    g.user доступен во view-функциях и шаблонах в рамках одного запроса.
    """
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        # sqlite3.Row позволяет обращаться к полям как к словарю: row['username']
        g.user = get_db().execute(
            'SELECT id, username, discriminator FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    """Выход пользователя: очищаем сессию и возвращаем на главную."""
    session.clear()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('main.index'))