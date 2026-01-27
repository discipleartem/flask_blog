# tests/base.py
"""Базовые классы и утилиты для тестов."""

from app.forms.csrf import generate_csrf_token, validate_csrf_token
from app.auth import hash_password


class BaseTestCase:
    """Базовый класс с общими методами для всех тестов."""

    def assert_csrf_validation(self, token, expected=True):
        """Унифицированная проверка CSRF валидации.

        Args:
            token: CSRF токен для проверки
            expected: Ожидаемый результат (True/False)
        """
        result = validate_csrf_token(token)
        assert (
            result is expected
        ), f"CSRF validation failed: expected {expected}, got {result}"

    def assert_csrf_token_generation(self):
        """Проверка генерации CSRF токена."""
        token = generate_csrf_token()
        assert token is not None
        assert len(token) > 0
        assert len(token) == 64  # SHA256 hex
        return token

    def create_test_user_data(
        self, username="test_user", discriminator=1234, password="test_pass"
    ):
        """Создание данных для тестового пользователя.

        Returns:
            dict: Данные пользователя с хэшированным паролем
        """
        hashed_pw, salt = hash_password(password)
        return {
            "username": username,
            "discriminator": discriminator,
            "password": password,
            "hashed_password": hashed_pw,
            "salt": salt,
        }

    def assert_form_validation_error(self, response, error_keywords=None):
        """Проверка наличия ошибок валидации в ответе.

        Args:
            response: Response объект
            error_keywords: Список ключевых слов для поиска в ошибке
        """
        assert response.status_code == 200
        response_text = response.data.decode("utf-8").lower()

        # Стандартные проверки ошибок
        error_indicators = [
            "alert-danger",
            "ошибка",
            "обязательно",
            "должно быть",
            "формат",
            "неверный",
        ]
        assert any(
            indicator in response_text for indicator in error_indicators
        ), f"No validation error found in response: {response_text[:200]}"

        # Дополнительные проверки по ключевым словам
        if error_keywords:
            for keyword in error_keywords:
                assert (
                    keyword.lower() in response_text
                ), f"Keyword '{keyword}' not found in error message"

    def assert_success_response(self, response, status_codes=None):
        """Проверка успешного ответа.

        Args:
            response: Response объект
            status_codes: Разрешенные коды успешного ответа
        """
        if status_codes is None:
            status_codes = [200, 302]  # OK или Redirect

        assert (
            response.status_code in status_codes
        ), f"Expected success status {status_codes}, got {response.status_code}"

    def setup_csrf_in_session(self, client, token_base="test_token_base"):
        """Установка CSRF токена в сессии клиента.

        Args:
            client: Test клиент
            token_base: База для генерации токена

        Returns:
            str: Сгенерированный токен
        """
        with client.session_transaction() as sess:
            sess["_csrf_token"] = token_base
        return generate_csrf_token()


class DatabaseTestHelper:
    """Хелпер для операций с базой данных в тестах."""

    @staticmethod
    def create_user_with_password(db, username, discriminator, password):
        """Создание пользователя с хэшированным паролем.

        Args:
            db: Объект базы данных
            username: Имя пользователя
            discriminator: Дискриминатор
            password: Пароль

        Returns:
            tuple: (hashed_password, salt)
        """
        hashed_pw, salt = hash_password(password)
        db.execute(
            "INSERT INTO user (username, discriminator, password, salt) "
            "VALUES (?, ?, ?, ?)",
            (username, discriminator, hashed_pw, salt),
        )
        return hashed_pw, salt

    @staticmethod
    def create_user_with_post(
        db, username, discriminator, password, post_title, post_content
    ):
        """Создание пользователя с постом для тестов.

        Args:
            db: Объект базы данных
            username: Имя пользователя
            discriminator: Дискриминатор
            password: Пароль
            post_title: Заголовок поста
            post_content: Содержание поста

        Returns:
            tuple: (user_id, post_id)
        """
        # Создаем пользователя
        hashed_pw, salt = hash_password(password)
        db.execute(
            "INSERT INTO user (username, discriminator, password, salt) "
            "VALUES (?, ?, ?, ?)",
            (username, discriminator, hashed_pw, salt),
        )
        db.commit()

        # Получаем ID пользователя
        user = db.execute(
            "SELECT id FROM user WHERE username = ? AND discriminator = ?",
            (username, discriminator),
        ).fetchone()

        user_id = user["id"] if user else None

        if user_id:
            # Создаем пост
            db.execute(
                "INSERT INTO post (title, content, author_id) VALUES (?, ?, ?)",
                (post_title, post_content, user_id),
            )
            db.commit()

            # Получаем ID поста
            post = db.execute(
                "SELECT id FROM post WHERE title = ? AND author_id = ?",
                (post_title, user_id),
            ).fetchone()

            post_id = post["id"] if post else None
            return user_id, post_id

        return user_id, None

    @staticmethod
    def cleanup_test_data(db, usernames=None, user_ids=None):
        """Очистка тестовых данных.

        Args:
            db: Объект базы данных
            usernames: Список имён пользователей для удаления
            user_ids: Список ID пользователей для удаления
        """
        if usernames:
            placeholders = ",".join("?" for _ in usernames)
            db.execute(
                f"DELETE FROM user WHERE username IN ({placeholders})",
                usernames,  # nosec: B608
            )

        if user_ids:
            placeholders = ",".join("?" for _ in user_ids)
            db.execute(
                f"DELETE FROM user WHERE id IN ({placeholders})", user_ids
            )  # nosec: B608

        db.commit()


class FormTestHelper:
    """Хелпер для тестирования форм."""

    @staticmethod
    def create_form_data_with_csrf(client, **kwargs):
        """Создание данных формы с CSRF токеном.

        Args:
            client: Test клиент
            **kwargs: Дополнительные поля формы

        Returns:
            dict: Данные формы с CSRF токеном
        """
        # В тестах используем фиксированный токен
        token = "test_csrf_token_for_testing"
        form_data = {"csrf_token": token}
        form_data.update(kwargs)
        return form_data

    @staticmethod
    def assert_form_fields_exist(form, *field_names):
        """Проверка наличия полей в форме.

        Args:
            form: Объект формы
            *field_names: Имена полей для проверки
        """
        for field_name in field_names:
            assert hasattr(form, field_name), f"Form missing field: {field_name}"
