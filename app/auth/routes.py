"""Маршруты авторизации."""

import sqlite3

from flask import flash, g, redirect, render_template, request, session, url_for

from app.auth import bp
from app.auth.utils import generate_discriminator, hash_password, verify_password
from app.db import get_db


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
                hashed_password, salt = hash_password(password)
                try:
                    db.execute(
                        'INSERT INTO user (username, discriminator, password, salt) VALUES (?, ?, ?, ?)',
                        (username, discriminator, hashed_password, salt),
                    )
                    db.commit()
                except sqlite3.IntegrityError:
                    error = 'Произошла ошибка при регистрации. Попробуйте еще раз.'
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

        if '#' not in username_with_tag:
            flash('Неверный формат логина. Используйте: Логин#1234', 'danger')
            return render_template('auth/login.html')

        parts = username_with_tag.rsplit('#', 1)
        username = parts[0]

        try:
            discriminator = int(parts[1])
        except ValueError:
            flash('Неверный формат логина. Используйте: Логин#1234', 'danger')
            return render_template('auth/login.html')

        user = db.execute(
            'SELECT * FROM user WHERE username = ? AND discriminator = ?',
            (username, discriminator),
        ).fetchone()

        if user is None or not verify_password(user['password'], password, user['salt']):
            flash('Неверный логин или пароль.', 'danger')
            return render_template('auth/login.html')

        session.clear()
        session['user_id'] = user['id']
        flash('Вы успешно вошли!', 'success')
        return redirect(url_for('main.index'))

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
    return redirect(url_for('main.index'))
