"""Маршруты авторизации.

Модуль предоставляет следующие функции:
- Регистрация пользователя с автоматической генерацией дискриминатора
- Аутентификация по формату username#0001 или admin
- Управление сессиями и cookie для запоминания пользователей
- Загрузка данных пользователя в контекст запроса
- Выход из системы

Особенности реализации:
- Используется Discord-стиль логинов с дискриминаторами
- Admin пользователь может входить без дискриминатора
- HttpOnly cookie для безопасного хранения последнего логина
- Поддержка автозаполнения форм браузера
"""

import sqlite3
from typing import Optional, Tuple

from flask import (
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    current_app,
    make_response,
    jsonify,
)

from app.auth import bp
from app.auth.utils import generate_discriminator, hash_password, verify_password
from app.db import get_db
from app.forms import RegistrationForm, LoginForm

# Константы для управления cookie
COOKIE_DAYS = 30
COOKIE_OPTIONS = {
    "max_age": COOKIE_DAYS * 24 * 60 * 60,
    "httponly": False,  # Нужно для доступа из JavaScript
    "secure": True,
    "samesite": "Strict",
}

# Cookie для хранения полных логинов
FULL_USERNAME_COOKIE = "full_usernames"

# Константы для валидации
ADMIN_USERNAME = "admin"
DISCRIMINATOR_FORMAT = "{:04d}"


def set_full_username_cookie(response, base_username: str, full_username: str) -> None:
    """Устанавливает cookie с полным логином для localStorage-подобной функциональности.

    Args:
        response: Flask response объект
        base_username: Базовый логин пользователя
        full_username: Полный логин с дискриминатором
    """
    import json

    # Получаем текущие данные из cookie
    existing_data = {}
    if FULL_USERNAME_COOKIE in request.cookies:
        try:
            existing_data = json.loads(request.cookies[FULL_USERNAME_COOKIE])
        except (json.JSONDecodeError, TypeError):
            existing_data = {}

    # Добавляем/обновляем логин
    existing_data[base_username.lower()] = full_username

    # Устанавливаем обновленное cookie
    response.set_cookie(
        FULL_USERNAME_COOKIE, json.dumps(existing_data), **COOKIE_OPTIONS
    )


def get_full_username_cookie(base_username: str) -> Optional[str]:
    """Получает полный логин из cookie.

    Args:
        base_username: Базовый логин

    Returns:
        Полный логин или None
    """
    import json

    if FULL_USERNAME_COOKIE not in request.cookies:
        return None

    try:
        data = json.loads(request.cookies[FULL_USERNAME_COOKIE])
        return data.get(base_username.lower())
    except (json.JSONDecodeError, TypeError):
        return None


def create_user_session(user_id: int) -> None:
    """Создаёт безопасную сессию для пользователя.

    Очищает предыдущие данные сессии и устанавливает новые.

    Args:
        user_id: ID пользователя из базы данных
    """
    session.clear()
    session["user_id"] = user_id
    session.permanent = True


def format_full_username(username: str, discriminator: int) -> str:
    """Форматирует полный логин с дискриминатором.

    Args:
        username: Базовое имя пользователя
        discriminator: Числовой дискриминатор (0 для admin)

    Returns:
        Полный логин в формате username#0000 или просто username для admin
    """
    return (
        f"{username}#{DISCRIMINATOR_FORMAT.format(discriminator)}"
        if discriminator > 0
        else username
    )


def get_prefilled_usernames() -> Tuple[str, str]:
    """Извлекает логины из cookie для автозаполнения формы.

    Возвращает кортеж из двух значений:
    - Полный логин (user#1234) для скрытого поля
    - Базовый логин (user) для видимого поля ввода

    Returns:
        Tuple[full_username, base_username]: Полный и базовый логины
    """
    # Используем новый cookie с полными логинами
    prefilled_full_username = ""
    prefilled_base_username = ""

    # Ищем любой сохраненный логин для автозаполнения
    if FULL_USERNAME_COOKIE in request.cookies:
        try:
            import json

            data = json.loads(request.cookies[FULL_USERNAME_COOKIE])
            if data:
                # Берем первый сохраненный логин для автозаполнения
                first_base = next(iter(data))
                prefilled_base_username = first_base
                prefilled_full_username = data[first_base]
        except (json.JSONDecodeError, TypeError):
            pass

    return prefilled_full_username, prefilled_base_username


def authenticate_admin(password: str) -> Tuple[Optional[dict], Optional[str]]:
    """Аутентифицирует admin пользователя.

    Особенности:
    - Admin может входить без дискриминатора
    - Если admin отсутствует в БД, создаётся автоматически
    - Пароль проверяется через конфигурацию приложения

    Args:
        password: Пароль для проверки

    Returns:
        Tuple[user_dict, error_message]: Данные пользователя или None,
        сообщение об ошибке или None
    """
    if password != current_app.config["ADMIN_PASSWORD"]:
        return None, "Неверный пароль для admin"

    db = get_db()
    admin_user = db.execute(
        "SELECT * FROM user WHERE username = ?", (ADMIN_USERNAME,)
    ).fetchone()

    # Создаём admin пользователя если его нет
    if admin_user is None:
        hashed_pw, salt = hash_password(password)
        db.execute(
            "INSERT INTO user (username, password, discriminator, salt) "
            "VALUES (?, ?, ?, ?)",
            (ADMIN_USERNAME, hashed_pw, 0, salt),
        )
        db.commit()
        admin_user = db.execute(
            "SELECT * FROM user WHERE username = ?", (ADMIN_USERNAME,)
        ).fetchone()

    return admin_user, None


def authenticate_user(
    username_to_check: str, password: str
) -> Tuple[Optional[dict], Optional[str]]:
    """Аутентифицирует обычного пользователя с поддержкой localStorage.

    Приоритеты:
    1. Если есть дискриминатор - точное совпадение
    2. Если нет дискриминатора - проверяем localStorage, потом fallback

    Args:
        username_to_check: Логин (может быть с дискриминатором или без)
        password: Пароль для проверки

    Returns:
        Tuple[user_dict, error_message]: Данные пользователя или None,
        сообщение об ошибке или None
    """
    db = get_db()

    # Случай 1: Введен полный логин с дискриминатором
    if "#" in username_to_check:
        try:
            username, tag_str = username_to_check.rsplit("#", 1)
            tag = int(tag_str)
        except (ValueError, IndexError):
            return None, "Неверный формат логина"

        user = db.execute(
            "SELECT * FROM user WHERE username = ? AND discriminator = ?",
            (username, tag),
        ).fetchone()

        if user is None:
            return None, "Неверный логин или пароль"

        if not verify_password(user["password"], password, user["salt"]):
            return None, "Неверный логин или пароль"

        return user, None

    # Случай 2: Введен только базовый логин (без дискриминатора)
    users = db.execute(
        "SELECT * FROM user WHERE username = ?", (username_to_check,)
    ).fetchall()

    if not users:
        return None, "Неверный логин или пароль"

    # Проверяем пароль для всех пользователей с таким логином
    valid_users = []
    for user in users:
        if verify_password(user["password"], password, user["salt"]):
            valid_users.append(user)

    if not valid_users:
        return None, "Неверный логин или пароль"

    # Если только один пользователь с правильным паролем - входим
    if len(valid_users) == 1:
        return valid_users[0], None

    # Если несколько пользователей с правильным паролем - отказываем
    # (требуется полный логин с дискриминатором)
    return None, (
        f"Найдено несколько аккаунтов с логином '{username_to_check}'. "
        "Пожалуйста, используйте полный логин с дискриминатором (например: user#1234)"
    )


@bp.route("/register", methods=("GET", "POST"))
def register() -> str:
    """Регистрация нового пользователя с автоматической генерацией дискриминатора.

    Процесс регистрации:
    1. Валидация формы (username, пароль)
    2. Проверка зарезервированных имён
    3. Генерация уникального дискриминатора
    4. Создание записи в БД с хэшированным паролем
    5. Автоматический вход и перенаправление

    Returns:
        HTML страница регистрации или перенаправление на главную
    """
    form = RegistrationForm(request.form)

    if request.method == "POST" and form.validate():
        username, password, validation_error = _extract_form_data(form)

        if validation_error:
            flash(validation_error, "danger")
            return render_template("auth/register.html", form=form)

        registration_result = _process_registration(username, password)

        if "error" in registration_result:
            flash(registration_result["error"], "danger")
        else:
            # Успешная регистрация с автоматическим входом
            return registration_result["response"]

    # Отображение ошибок валидации формы
    elif request.method == "POST":
        _display_form_errors(form)

    return render_template("auth/register.html", form=form)


def _extract_form_data(form: RegistrationForm) -> Tuple[str, str, Optional[str]]:
    """Извлекает и валидирует данные из формы регистрации.

    Args:
        form: Объект формы регистрации

    Returns:
        Tuple[username, password, error]: Данные формы и ошибка валидации
    """
    username = form.username.data.strip()
    password = form.password.data

    # Проверка зарезервированного имени
    if username.lower() == ADMIN_USERNAME:
        return username, password, f"Имя {ADMIN_USERNAME} зарезервировано системой"

    return username, password, None


def _process_registration(username: str, password: str) -> dict:
    """Обрабатывает процесс регистрации пользователя.

    Args:
        username: Имя пользователя
        password: Пароль

    Returns:
        dict: Результат регистрации с error или response
    """
    db = get_db()

    # Генерация уникального дискриминатора
    new_discriminator = generate_discriminator(db, username)

    if new_discriminator is None:
        return {"error": f"К сожалению, имя {username} перегружено. Попробуйте другое."}

    try:
        # Создание пользователя в БД
        user_id = _create_user_in_db(db, username, password, new_discriminator)

        # Автоматический вход
        create_user_session(user_id)

        # Создание ответа с cookie для автозаполнения
        response = make_response(redirect(url_for("main.index")))
        full_username = format_full_username(username, new_discriminator)

        # Сохраняем полный логин в cookie для localStorage-подобной функциональности
        set_full_username_cookie(response, username, full_username)

        flash(f"Добро пожаловать {full_username}!", "success")

        return {
            "response": response,
            "full_username": full_username,
            "base_username": username,
        }

    except sqlite3.IntegrityError:
        return {"error": "Ошибка при регистрации. Возможно, имя занято."}


def _create_user_in_db(db, username: str, password: str, discriminator: int) -> int:
    """Создаёт запись пользователя в базе данных.

    Args:
        db: Объект подключения к БД
        username: Имя пользователя
        password: Пароль
        discriminator: Дискриминатор

    Returns:
        int: ID созданного пользователя
    """
    hashed_pw, salt = hash_password(password)
    cursor = db.execute(
        "INSERT INTO user (username, password, discriminator, salt) "
        "VALUES (?, ?, ?, ?)",
        (username, hashed_pw, discriminator, salt),
    )
    db.commit()
    return cursor.lastrowid


def _display_form_errors(form: RegistrationForm) -> None:
    """Отображает ошибки валидации формы.

    Args:
        form: Объект формы с ошибками
    """
    for field_name, field_errors in form.errors.items():
        for error in field_errors:
            flash(error, "danger")


@bp.route("/login", methods=("GET", "POST"))
def login() -> str:
    """Вход пользователя с поддержкой дискриминаторов.

    Форматы входа:
    - Username#0000: для обычных пользователей
    - admin: для администратора (без дискриминатора)

    Особенности:
    - Автозаполнение из cookie
    - Приоритет скрытого поля с полным логином
    - Сохранение последнего успешного логина в cookie

    Returns:
        HTML страница входа или перенаправление на главную
    """
    prefilled_username, prefilled_base_username = get_prefilled_usernames()
    form = LoginForm(request.form)

    if request.method == "POST" and form.validate():
        login_result = _process_login_attempt()

        if login_result["success"]:
            return login_result["response"]
        else:
            flash(login_result["error"], "danger")

    # Отображение ошибок валидации формы
    elif request.method == "POST":
        _display_form_errors(form)

    return render_template(
        "auth/login.html",
        form=form,
        prefilled_username=prefilled_username,
        prefilled_base_username=prefilled_base_username,
    )


def _process_login_attempt() -> dict:
    """Обрабатывает попытку входа пользователя.

    Returns:
        dict: Результат входа с success/response или error
    """
    # Извлечение данных формы
    raw_username = request.form.get("username", "").strip()
    full_username_hidden = request.form.get("full_username", "").strip()
    password = request.form.get("password", "")

    # Определение логина для проверки (приоритет скрытому полю)
    username_to_check = _determine_username_for_check(
        raw_username, full_username_hidden
    )

    # Обработка входа admin
    if username_to_check.lower() == ADMIN_USERNAME:
        return _handle_admin_login(password)

    # Обработка входа обычного пользователя
    return _handle_user_login(username_to_check, password)


def _determine_username_for_check(raw_username: str, full_username_hidden: str) -> str:
    """Определяет какой логин использовать для аутентификации.

    Приоритет: скрытое поле с полным логином > cookie > видимое поле

    Args:
        raw_username: Логин из видимого поля
        full_username_hidden: Логин из скрытого поля

    Returns:
        str: Логин для проверки
    """
    # Сначала проверяем скрытое поле (JavaScript)
    if full_username_hidden and "#" in full_username_hidden:
        return full_username_hidden

    # Потом проверяем cookie
    cookie_full_username = get_full_username_cookie(raw_username)
    if cookie_full_username and "#" in cookie_full_username:
        return cookie_full_username

    # В конце используем введенный логин
    return raw_username


def _handle_admin_login(password: str) -> dict:
    """Обрабатывает вход admin пользователя.

    Args:
        password: Пароль для проверки

    Returns:
        dict: Результат входа
    """
    admin_user, error = authenticate_admin(password)

    if admin_user:
        create_user_session(admin_user["id"])

        response = make_response(redirect(url_for("main.index")))
        # Для admin тоже сохраняем в full_usernames
        set_full_username_cookie(response, ADMIN_USERNAME, ADMIN_USERNAME)
        flash("Добро пожаловать, admin!", "success")

        return {"success": True, "response": response}

    return {"success": False, "error": error}


def _handle_user_login(username: str, password: str) -> dict:
    """Обрабатывает вход обычного пользователя.

    Args:
        username: Логин с дискриминатором
        password: Пароль

    Returns:
        dict: Результат входа
    """
    user, error = authenticate_user(username, password)

    if user:
        create_user_session(user["id"])

        full_username = format_full_username(user["username"], user["discriminator"])
        response = make_response(redirect(url_for("main.index")))

        # Обновляем cookie с полными логинами
        set_full_username_cookie(response, user["username"], full_username)

        return {"success": True, "response": response}

    return {"success": False, "error": error}


@bp.before_app_request
def load_logged_in_user() -> None:
    """Загружает текущего пользователя в контекст запроса.

    Выполняется перед каждым запросом к приложению.
    g.user доступен во view-функциях и шаблонах в рамках одного запроса.

    Returns:
        None
    """
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        # Используем sqlite3.Row для доступа к полям как к словарю
        g.user = (
            get_db()
            .execute(
                "SELECT id, username, discriminator FROM user WHERE id = ?", (user_id,)
            )
            .fetchone()
        )


@bp.route("/logout")
def logout() -> str:
    """Выход пользователя из системы.

    Очищает сессию пользователя и перенаправляет на главную страницу.

    Returns:
        Redirect на главную страницу
    """
    session.clear()
    flash("Вы вышли из системы.", "info")
    return redirect(url_for("main.index"))


@bp.route("/api/get-user-info")
def get_user_info() -> dict:
    """API endpoint для получения информации о текущем пользователе.

    Возвращает полный логин для сохранения в localStorage после регистрации.

    Returns:
        JSON с информацией о пользователе или ошибку
    """
    user_id = session.get("user_id")

    if not user_id:
        return {"error": "Пользователь не авторизован"}, 401

    db = get_db()
    user = db.execute(
        "SELECT username, discriminator FROM user WHERE id = ?", (user_id,)
    ).fetchone()

    if not user:
        return {"error": "Пользователь не найден"}, 404

    full_username = format_full_username(user["username"], user["discriminator"])

    return {
        "base_username": user["username"],
        "full_username": full_username,
        "discriminator": user["discriminator"],
    }
