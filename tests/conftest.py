# tests/conftest.py
"""Фикстуры для тестирования Flask приложения."""

import os
import tempfile
import pytest
import warnings
import sys

# Полное подавление предупреждений о временных метках
if not sys.warnoptions:
    warnings.simplefilter("ignore")
    warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*default timestamp converter.*")

from app import create_app
from app.db.db import get_db, init_db


@pytest.fixture
def app():
    """Создает тестовое приложение с временной БД."""
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
        'SECRET_KEY': 'test-secret-key-for-testing',
        'WTF_CSRF_ENABLED': False,  # Отключаем CSRF для тестов
    })

    with app.app_context():
        init_db()
        # Создаем тестового пользователя
        db = get_db()
        from app.auth import hash_password
        hashed_pw, salt = hash_password('test_pass')
        db.execute(
            'INSERT INTO user (username, discriminator, password, salt) VALUES (?, ?, ?, ?)',
            ('test_user', 1234, hashed_pw, salt),
        )
        db.commit()

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Тестовый клиент для отправки запросов."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI runner для тестирования команд."""
    return app.test_cli_runner()


@pytest.fixture
def auth(client):
    """Фикстура для аутентификации."""
    return AuthActions(client)


class AuthActions:
    """Вспомогательный класс для действий аутентификации в тестах."""

    def __init__(self, client):
        self._client = client

    def login(self, username='test_user#1234', password='test_pass', follow_redirects=False):
        """Выполнение входа пользователя."""
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password},
            follow_redirects=follow_redirects
        )

    def logout(self):
        """Выполнение выхода пользователя."""
        return self._client.get('/auth/logout')

    def register(self, username='new_user', password='new_pass123', follow_redirects=False):
        """Регистрация нового пользователя."""
        return self._client.post(
            '/auth/register',
            data={'username': username, 'password': password},
            follow_redirects=follow_redirects
        )


@pytest.fixture
def sample_user_data():
    """Данные для тестового пользователя."""
    return {
        'username': 'sample_user',
        'password': 'sample_password',
        'discriminator': 9999
    }


@pytest.fixture
def sample_post_data():
    """Данные для тестового поста."""
    return {
        'title': 'Test Post Title',
        'content': 'This is a test post content for testing purposes.'
    }


@pytest.fixture
def mock_csrf_token():
    """Мок CSRF токена для тестов."""
    return 'test-csrf-token-12345'


@pytest.fixture(scope='session')
def test_database():
    """Создает тестовую базу данных для всей сессии."""
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
        'SECRET_KEY': 'session-test-secret-key',
    })
    
    with app.app_context():
        init_db()
        
        # Создаем тестовых пользователей
        db = get_db()
        from app.auth import hash_password
        
        users = [
            ('admin_user', 1000, 'admin_pass'),
            ('regular_user', 2000, 'user_pass'),
            ('moderator_user', 3000, 'mod_pass'),
        ]
        
        for username, discriminator, password in users:
            hashed_pw, salt = hash_password(password)
            db.execute(
                'INSERT INTO user (username, discriminator, password, salt) VALUES (?, ?, ?, ?)',
                (username, discriminator, hashed_pw, salt)
            )
        
        db.commit()
    
    yield db_path
    
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def app_with_test_db(test_database):
    """Приложение с готовой тестовой базой данных."""
    app = create_app({
        'TESTING': True,
        'DATABASE': test_database,
        'SECRET_KEY': 'app-test-secret-key',
        'WTF_CSRF_ENABLED': False,
    })
    
    return app


@pytest.fixture
def client_with_test_db(app_with_test_db):
    """Клиент с готовой тестовой базой данных."""
    return app_with_test_db.test_client()


# Маркеры для разных типов тестов
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.security = pytest.mark.security
pytest.mark.database = pytest.mark.database
pytest.mark.slow = pytest.mark.slow
