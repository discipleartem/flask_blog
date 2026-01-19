# tests/test_auth.py

from app.auth import hash_password, verify_password, generate_discriminator
from app.db import get_db


class TestPasswordHashing:
    """Тесты для функций хэширования паролей."""

    def test_hash_password_returns_hex_string(self):
        """Хэш пароля должен быть hex-строкой."""
        hashed, salt = hash_password('password123')
        assert isinstance(hashed, str)
        # Проверяем, что это валидный hex
        bytes.fromhex(hashed)

    def test_hash_password_creates_salt(self):
        """Функция должна создавать соль, если она не передана."""
        hashed, salt = hash_password('password123')
        assert salt is not None
        assert len(salt) == 16

    def test_hash_password_uses_provided_salt(self):
        """Функция должна использовать переданную соль."""
        custom_salt = b'1234567890123456'
        hashed1, _ = hash_password('password123', custom_salt)
        hashed2, _ = hash_password('password123', custom_salt)
        assert hashed1 == hashed2

    def test_different_passwords_different_hashes(self):
        """Разные пароли должны давать разные хэши."""
        hashed1, salt = hash_password('password123')
        hashed2, _ = hash_password('password456', salt)
        assert hashed1 != hashed2

    def test_verify_password_correct(self):
        """Проверка правильного пароля."""
        hashed, _ = hash_password('mypassword')
        assert verify_password(hashed, 'mypassword') is True

    def test_verify_password_incorrect(self):
        """Проверка неправильного пароля."""
        hashed, _ = hash_password('mypassword')
        assert verify_password(hashed, 'wrongpassword') is False


class TestGenerateDiscriminator:
    """Тесты для генерации дискриминатора."""

    def test_generate_discriminator_new_user(self, app):
        """Генерация дискриминатора для нового username."""
        with app.app_context():
            db = get_db()
            discriminator = generate_discriminator(db, 'newuser')
            assert discriminator is not None
            assert 1 <= discriminator <= 9999

    def test_generate_discriminator_existing_user(self, app):
        """Генерация дискриминатора для существующего username."""
        with app.app_context():
            db = get_db()
            # testuser#1234 уже существует
            discriminator = generate_discriminator(db, 'testuser')
            assert discriminator is not None
            assert discriminator != 1234  # Не должен совпадать с существующим


class TestRegister:
    """Тесты для регистрации."""

    def test_register_page_loads(self, client):
        """Страница регистрации должна загружаться."""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert 'Регистрация'.encode('utf-8') in response.data

    def test_register_success(self, client, app):
        """Успешная регистрация нового пользователя."""
        response = client.post(
            '/auth/register',
            data={'username': 'newuser', 'password': 'newpass'},
            follow_redirects=True
        )
        assert response.status_code == 200
        assert 'Регистрация успешна'.encode('utf-8') in response.data

        # Проверяем, что пользователь создан в БД
        with app.app_context():
            db = get_db()
            user = db.execute(
                'SELECT * FROM user WHERE username = ?', ('newuser',)
            ).fetchone()
            assert user is not None

    def test_register_empty_username(self, client):
        """Регистрация с пустым логином."""
        response = client.post(
            '/auth/register',
            data={'username': '', 'password': 'password123'}
        )
        assert 'Требуется логин'.encode('utf-8') in response.data

    def test_register_empty_password(self, client):
        """Регистрация с пустым паролем."""
        response = client.post(
            '/auth/register',
            data={'username': 'someuser', 'password': ''}
        )
        assert 'Требуется пароль'.encode('utf-8') in response.data

    def test_register_short_password(self, client):
        """Регистрация со слишком коротким паролем."""
        response = client.post(
            '/auth/register',
            data={'username': 'someuser', 'password': '123'}
        )
        assert 'не менее 4 символов'.encode('utf-8') in response.data


class TestLogin:
    """Тесты для входа в систему."""

    def test_login_page_loads(self, client):
        """Страница входа должна загружаться."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert 'Вход'.encode('utf-8') in response.data

    def test_login_success(self, client, auth):
        """Успешный вход."""
        response = auth.login()
        assert response.status_code == 302  # Редирект

        # Проверяем, что сессия установлена
        with client.session_transaction() as sess:
            assert 'user_id' in sess

    def test_login_success_redirect(self, client, auth):
        """После входа должен быть редирект на главную."""
        response = auth.login(follow_redirects=False)
        assert response.status_code == 302
        assert response.headers['Location'] == '/'

    def test_login_invalid_format_no_hash(self, client):
        """Вход с неверным форматом (без #)."""
        response = client.post(
            '/auth/login',
            data={'username': 'testuser1234', 'password': 'testpass'}
        )
        assert 'Неверный формат логина'.encode('utf-8') in response.data

    def test_login_invalid_format_bad_discriminator(self, client):
        """Вход с неверным дискриминатором (не число)."""
        response = client.post(
            '/auth/login',
            data={'username': 'testuser#abcd', 'password': 'testpass'}
        )
        assert 'Неверный формат логина'.encode('utf-8') in response.data

    def test_login_wrong_password(self, client):
        """Вход с неверным паролем."""
        response = client.post(
            '/auth/login',
            data={'username': 'testuser#1234', 'password': 'wrongpass'}
        )
        assert 'Неверный логин или пароль'.encode('utf-8') in response.data

    def test_login_nonexistent_user(self, client):
        """Вход с несуществующим пользователем."""
        response = client.post(
            '/auth/login',
            data={'username': 'nouser#0000', 'password': 'anypass'}
        )
        assert 'Неверный логин или пароль'.encode('utf-8') in response.data


class TestLogout:
    """Тесты для выхода из системы."""

    def test_logout(self, client, auth):
        """Выход из системы очищает сессию."""
        auth.login()

        # Проверяем, что залогинены
        with client.session_transaction() as sess:
            assert 'user_id' in sess

        response = auth.logout()
        assert response.status_code == 302

        # Проверяем, что сессия очищена
        with client.session_transaction() as sess:
            assert 'user_id' not in sess


class TestLoginRequired:
    """Тесты для декоратора login_required."""

    def test_load_logged_in_user(self, client, auth, app):
        """Загрузка залогиненного пользователя в g."""
        auth.login()

        with client:
            client.get('/')
            from flask import g
            assert g.user is not None
            assert g.user['username'] == 'testuser'

    def test_load_logged_in_user_anonymous(self, client, app):
        """Для незалогиненного пользователя g.user = None."""
        with client:
            client.get('/')
            from flask import g
            assert g.user is None
