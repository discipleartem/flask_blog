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
)

from app.auth import bp
from app.auth.utils import generate_discriminator, hash_password, verify_password
from app.db import get_db
from app.forms import RegistrationForm, LoginForm

# Константы для управления cookie
COOKIE_DAYS = 30
COOKIE_OPTIONS = {
    "max_age": COOKIE_DAYS * 24 * 60 * 60,
    "httponly": True,
    "secure": True,
    "samesite": "Strict",
}

# Константы для валидации
ADMIN_USERNAME = "admin"
DISCRIMINATOR_FORMAT = "{:04d}"


def set_auth_cookie(response, username: str) -> None:
    """Устанавливает HttpOnly cookie с логином пользователя для автозаполнения.

    Args:
        response: Flask response объект
        username: Полный логин пользователя (с дискриминатором или admin)
    """
    response.set_cookie("last_username", username, **COOKIE_OPTIONS)


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
    prefilled_username = request.cookies.get("last_username", "")
    prefilled_base_username = (
        prefilled_username.split("#")[0] if prefilled_username else ""
    )
    return prefilled_username, prefilled_base_username


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
    """Аутентифицирует обычного пользователя по логину с дискриминатором.

    Проверяет формат логина username#0000 и ищет соответствующую запись в БД.

    Args:
        username_to_check: Логин в формате username#0000
        password: Пароль для проверки

    Returns:
        Tuple[user_dict, error_message]: Данные пользователя или None,
        сообщение об ошибке или None
    """
    if "#" not in username_to_check:
        return None, "Неверный формат логина"

    try:
        username, tag_str = username_to_check.rsplit("#", 1)
        tag = int(tag_str)
    except (ValueError, IndexError):
        return None, "Неверный формат логина"

    db = get_db()
    user = db.execute(
        "SELECT * FROM user WHERE username = ? AND discriminator = ?", (username, tag)
    ).fetchone()

    if user is None:
        return None, "Неверный логин или пароль"

    if not verify_password(user["password"], password, user["salt"]):
        return None, "Неверный логин или пароль"

    return user, None


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
        set_auth_cookie(response, full_username)

        flash(f"Добро пожаловать {full_username}!", "success")

        return {"response": response}

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

    Приоритет: скрытое поле с полным логином > видимое поле

    Args:
        raw_username: Логин из видимого поля
        full_username_hidden: Логин из скрытого поля

    Returns:
        str: Логин для проверки
    """
    return (
        full_username_hidden
        if full_username_hidden and "#" in full_username_hidden
        else raw_username
    )


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
        set_auth_cookie(response, ADMIN_USERNAME)
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
        set_auth_cookie(response, full_username)

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
