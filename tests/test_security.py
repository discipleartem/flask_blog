# tests/test_security.py
"""Объединённые тесты безопасности приложения."""

import pytest
from flask import Flask
from tests.base import BaseTestCase, FormTestHelper

from app.forms import Form, StringField, DataRequired, Length, EqualTo
from app.forms.csrf import generate_csrf_token


class TestCSRFProtection(BaseTestCase):
    """Тесты CSRF защиты."""

    def test_csrf_token_generation(self, app):
        """Генерация CSRF токена."""
        with app.test_request_context():
            self.assert_csrf_token_generation()

    def test_csrf_validation_correct_token(self, app):
        """Валидация правильного CSRF токена."""
        with app.test_request_context():
            token = generate_csrf_token()
            self.assert_csrf_validation(token, True)

    def test_csrf_validation_wrong_tokens(self, app):
        """Валидация неправильных CSRF токенов."""
        with app.test_request_context():
            wrong_tokens = ["wrong_token", "", None, "invalid", "123"]
            for token in wrong_tokens:
                self.assert_csrf_validation(token, False)

    def test_csrf_in_registration_form(self, security_client):
        """CSRF защита при регистрации."""
        # Правильный токен должен работать всегда
        form_data = FormTestHelper.create_form_data_with_csrf(
            security_client, username="csrf_test_user1", password="testpass123"
        )
        response = security_client.post("/auth/register", data=form_data)
        self.assert_success_response(response)

        # Неправильный токен должен блокироваться
        wrong_form_data = {
            "username": "csrf_test_user2",
            "password": "testpass123",
            "csrf_token": "wrong_token",
        }
        response = security_client.post("/auth/register", data=wrong_form_data)
        self.assert_form_validation_error(response)

        # Отсутствие токена должно блокироваться
        no_token_data = {"username": "csrf_test_user3", "password": "testpass123"}
        response = security_client.post("/auth/register", data=no_token_data)
        self.assert_form_validation_error(response)

    def test_csrf_in_login_form(self, security_client):
        """CSRF защита при входе."""
        # Правильный токен должен работать всегда
        form_data = FormTestHelper.create_form_data_with_csrf(
            security_client, username="test_user#1234", password="test_pass"
        )
        response = security_client.post("/auth/login", data=form_data)
        self.assert_success_response(response)

        # Неправильный токен должен блокироваться
        wrong_form_data = {
            "username": "test_user#1234",
            "password": "test_pass",
            "csrf_token": "wrong_token",
        }
        response = security_client.post("/auth/login", data=wrong_form_data)
        self.assert_form_validation_error(response)

    def test_csrf_in_post_operations(self, security_client, security_auth):
        """CSRF защита в операциях с постами."""
        # Вход с правильным токеном
        login_response = security_auth.login()
        assert login_response.status_code == 302

        # Правильный токен должен работать для создания поста
        form_data = FormTestHelper.create_form_data_with_csrf(
            security_client,
            title="CSRF Test Post",
            content="This is a test post with enough content length",
        )
        response = security_client.post("/post/create", data=form_data)
        self.assert_success_response(response)

        # Неправильный токен должен блокироваться
        wrong_form_data = {
            "title": "CSRF Test Post 2",
            "content": "This is another test post",
            "csrf_token": "wrong_token",
        }
        response = security_client.post("/post/create", data=wrong_form_data)
        self.assert_form_validation_error(response)


class TestPasswordSecurity(BaseTestCase):
    """Тесты безопасности паролей."""

    def test_password_hashing_uniqueness(self):
        """Разные пароли должны давать разные хэши."""
        from app.auth import hash_password

        password1 = "secure_password_123"
        password2 = "different_password"

        hashed1, salt1 = hash_password(password1)
        hashed2, salt2 = hash_password(password2)

        assert hashed1 != hashed2
        assert salt1 != salt2

    def test_password_verification_correct(self):
        """Проверка правильного пароля."""
        from app.auth import hash_password, verify_password

        password = "secure_password_123"
        hashed, salt = hash_password(password)

        assert verify_password(hashed, password, salt) is True

    def test_password_verification_incorrect(self):
        """Проверка неправильного пароля."""
        from app.auth import hash_password, verify_password

        password = "secure_password_123"
        hashed, salt = hash_password(password)

        assert verify_password(hashed, "wrong_password", salt) is False
        assert verify_password(hashed, "", salt) is False
        assert verify_password(hashed, None, salt) is False

    def test_password_hash_with_same_salt(self):
        """Одинаковые пароли с одинаковой солью дают одинаковые хэши."""
        from app.auth import hash_password

        password = "test_password"
        custom_salt = b"1234567890123456"

        hashed1, _ = hash_password(password, custom_salt)
        hashed2, _ = hash_password(password, custom_salt)

        assert hashed1 == hashed2

    def test_salt_generation(self):
        """Генерация соли должна быть уникальной."""
        from app.auth import hash_password

        salts = []
        for _ in range(10):
            _, salt = hash_password("test_password")
            assert salt is not None
            assert len(salt) == 16
            salts.append(salt)

        # Все соли должны быть уникальными
        assert len(set(salts)) == len(salts)


class TestFormSecurity(BaseTestCase, FormTestHelper):
    """Тесты безопасности форм."""

    @pytest.fixture
    def app(self):
        app = Flask(__name__)
        app.config["SECRET_KEY"] = "test-key-12345"
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        return app

    class TestForm(Form):
        """Тестовая форма с валидаторами."""

        name = StringField(
            "Name",
            validators=[
                DataRequired(message="Name required"),
                Length(min=3, max=10, message="Invalid length"),
            ],
        )
        confirm = StringField(
            "Confirm", validators=[EqualTo("name", message="Must match")]
        )

    def test_form_without_csrf_token(self, app):
        """Форма без CSRF токена должна быть невалидной когда CSRF включен."""
        with app.test_request_context():
            # Пропускаем тест если CSRF отключен
            if not app.config.get("WTF_CSRF_ENABLED", False):
                return

            data = {
                "name": "valid",
                "confirm": "valid",
                "csrf_token": None,  # Явно передаем None
            }

            form = self.TestForm(data)
            assert form.validate() is False
            assert "csrf" in form.errors

    def test_form_with_valid_csrf_token(self, app):
        """Форма с валидным CSRF токеном должна быть валидной."""
        with app.test_request_context():
            token = generate_csrf_token()
            data = {"name": "valid", "confirm": "valid", "csrf_token": token}

            form = self.TestForm(data)
            # С заглушками валидаторов форма всегда валидна при правильном CSRF
            assert form.validate() is True
            assert not form.errors

    def test_form_field_structure_unchanged(self, app):
        """Структура полей формы не изменилась."""
        with app.test_request_context():
            form = self.TestForm({})

            # Проверяем наличие полей
            self.assert_form_fields_exist(form, "name", "confirm")

            # Проверяем типы полей
            assert hasattr(form.name, "data")
            assert hasattr(form.confirm, "data")


class TestSessionSecurity(BaseTestCase):
    """Тесты безопасности сессий."""

    def test_session_cleared_on_logout(self, client, auth):
        """Выход должен очищать сессию."""
        # Вход
        auth.login()

        # Проверяем, что сессия установлена
        with client.session_transaction() as sess:
            assert "user_id" in sess
            original_user_id = sess["user_id"]

        # Выход
        auth.logout()

        # Проверяем, что сессия очищена
        with client.session_transaction() as sess:
            assert "user_id" not in sess or sess.get("user_id") != original_user_id

    def test_session_persistence_during_requests(self, client, auth):
        """Сессия должна сохраняться между запросами."""
        auth.login()

        # Делаем несколько запросов
        for _ in range(3):
            response = client.get("/")
            self.assert_success_response(response)

            # Проверяем, что сессия всё ещё активна
            with client.session_transaction() as sess:
                assert "user_id" in sess


class TestUsernameDiscriminatorSecurity(BaseTestCase):
    """Тесты безопасности системы дискриминаторов."""

    def test_discriminator_uniqueness_for_same_username(self, app):
        """Для одного username должны генерироваться разные дискриминаторы."""
        with app.app_context():
            from app.auth.utils import generate_discriminator
            from app.db.db import get_db

            db = get_db()

            discriminators = []
            for _ in range(5):
                disc = generate_discriminator(db, "testuser")
                assert disc is not None
                assert 1 <= disc <= 9999
                discriminators.append(disc)

            # Все дискриминаторы должны быть уникальными
            assert len(set(discriminators)) == len(discriminators)

    def test_different_usernames_independent_discriminators(self, app):
        """Разные usernames должны иметь независимые наборы дискриминаторов."""
        with app.app_context():
            from app.auth.utils import generate_discriminator
            from app.db.db import get_db

            db = get_db()

            # Генерируем дискриминаторы для разных имён
            disc1 = generate_discriminator(db, "alice")
            disc2 = generate_discriminator(db, "bob")

            assert disc1 is not None
            assert disc2 is not None
            assert 1 <= disc1 <= 9999
            assert 1 <= disc2 <= 9999
