"""Маршруты авторизации.

Содержит:
- регистрацию пользователя (с генерацией дискриминатора),
- вход по формату username#0001,
- загрузку пользователя в g.user для каждого запроса,
- выход (logout).
"""

import sqlite3

from flask import flash, g, redirect, render_template, request, session, url_for, current_app

from app.auth import bp
from app.auth.utils import generate_discriminator, hash_password, verify_password
from app.db import get_db


@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Регистрация нового пользователя.

    Валидация:
    - username обязателен и не содержит '#'
    - пароль минимум 4 символа
    - имя 'admin' зарезервировано

    При успехе создаём запись в таблице user и предлагаем войти.
    """
    if request.method == 'POST':
        # .strip() убирает случайные пробелы вокруг имени
        username = request.form['username'].strip()
        password = request.form['password']
        db = get_db()
        error = None

        # Базовые проверки ввода
        if not username:
            error = 'Требуется логин'
        elif not password:
            error = 'Требуется пароль'
        elif len(password) < 4:
            error = 'Пароль должен содержать не менее 4 символов'
        elif '#' in username:
            # Символ '#' зарезервирован под разделитель тега (discriminator)
            error = 'Имя пользователя не должно содержать символ #.'
        elif username.lower() == 'admin':
            # Имя admin зарезервировано для специального пользователя
            error = 'Имя admin зарезервировано системой'

        if error is None:
            # Генерация уникального дискриминатора (1..9999) для одинаковых username
            new_tag = generate_discriminator(db, username)

            if new_tag is None:
                # Случай, когда для username заняты все теги
                error = f"К сожалению, имя {username} перегружено. Попробуйте другое."
            else:
                try:
                    # Пароль храним только в виде хэша с солью
                    hashed_pw, salt = hash_password(password)
                    db.execute(
                        "INSERT INTO user (username, password, discriminator, salt) VALUES (?, ?, ?, ?)",
                        (username, hashed_pw, new_tag, salt),
                    )
                    db.commit()
                    flash(f'Добро пожаловать {username}#{new_tag:04d}', 'success')
                    # Передаем данные нового пользователя в форму входа
                    full_username = f"{username}#{new_tag:04d}"
                    return redirect(url_for("auth.login", username=full_username))
                except sqlite3.IntegrityError:
                    # На случай уникальных ограничений в схеме БД
                    error = "Ошибка при регистрации. Возможно, имя занято."

        if error:
            flash(error, 'danger')

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Вход пользователя.

    Ожидаемый формат логина: Username#0001
    (где 0001 — discriminator, хранимый в БД как число).
    
    Особый случай: admin может входить без дискриминатора.
    """
    # Получаем username из параметров URL для автозаполнения после регистрации
    prefilled_username = request.args.get('username', '')
    
    if request.method == 'POST':
        raw_username = request.form['username'].strip()
        password = request.form['password']
        db = get_db()
        error = None

        # Особый случай для admin: вход без дискриминатора
        if raw_username.lower() == 'admin':
            # Проверяем пароль admin из конфигурации
            if password == current_app.config['ADMIN_PASSWORD']:
                # Проверяем, существует ли admin в БД
                admin_user = db.execute(
                    'SELECT * FROM user WHERE username = ?', ('admin',)
                ).fetchone()
                
                if admin_user is None:
                    # Создаем admin пользователя с discriminator = 0
                    hashed_pw, salt = hash_password(password)
                    db.execute(
                        "INSERT INTO user (username, password, discriminator, salt) VALUES (?, ?, ?, ?)",
                        ('admin', hashed_pw, 0, salt),
                    )
                    db.commit()
                    admin_user = db.execute(
                        'SELECT * FROM user WHERE username = ?', ('admin',)
                    ).fetchone()
                
                # Успешный вход admin
                session.clear()
                session['user_id'] = admin_user['id']
                session.permanent = True
                flash('Добро пожаловать, admin!', 'success')
                return redirect(url_for('main.index'))
            else:
                error = 'Неверный пароль для admin'
        
        # Обычный вход с дискриминатором
        elif "#" in raw_username:
            parts = raw_username.rsplit("#", 1)
            username, tag_str = parts[0], parts[1]
            try:
                tag = int(tag_str)
                # Ищем конкретного пользователя по (username, discriminator)
                user = db.execute(
                    'SELECT * FROM user WHERE username = ? AND discriminator = ?',
                    (username, tag)
                ).fetchone()
            except (ValueError, IndexError):
                error = 'Неверный формат логина'
                user = None
        else:
            error = 'Неверный формат логина'
            user = None

        # Проверка найденного пользователя и пароля (для обычных пользователей)
        if error is None and raw_username.lower() != 'admin':
            if user is None:
                error = 'Неверный логин или пароль'
            elif not verify_password(user['password'], password, user['salt']):
                error = 'Неверный логин или пароль'

        # Успешный вход: кладём user_id в сессию
        if error is None and raw_username.lower() != 'admin':
            session.clear()
            session['user_id'] = user['id']
            session.permanent = True
            return redirect(url_for('main.index'))

        flash(error, 'danger')

    return render_template('auth/login.html', prefilled_username=prefilled_username)


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
