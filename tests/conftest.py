# tests/conftest.py
"""Фикстуры для тестирования Flask приложения."""

import os
import tempfile
import pytest
import warnings
import sys
import re
from typing import Dict, Any

# Полное подавление предупреждений о временных метках
if not sys.warnoptions:
    warnings.simplefilter("ignore")
    warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*default timestamp converter.*")

from app import create_app
from app.db.db import get_db, init_db


def _create_test_app(config: Dict[str, Any]) -> Any:
    """Вспомогательная функция для создания тестового приложения."""
    db_fd, db_path = tempfile.mkstemp()
    
    app_config = {
        'TESTING': True,
        'DATABASE': db_path,
        'SECRET_KEY': 'test-secret-key-for-testing',
        'ADMIN_PASSWORD': 'test_admin_password',
        **config
    }
    
    app = create_app(app_config)
    
    with app.app_context():
        init_db()
        _create_test_data()
    
    return app, db_fd, db_path


def _create_test_data():
    """Создает тестовые данные в базе."""
    db = get_db()
    from app.auth import hash_password
    
    # Создаем тестового пользователя
    hashed_pw, salt = hash_password('test_pass')
    db.execute(
        'INSERT INTO user (username, discriminator, password, salt) VALUES (?, ?, ?, ?)',
        ('test_user', 1234, hashed_pw, salt),
    )
    db.commit()
    
    # Создаем тестовые посты
    user_id = 1  # ID первого созданного пользователя
    test_posts = [
        ('Тестовый пост 1', 'Содержание первого тестового поста', user_id),
        ('Тестовый пост 2', 'Содержание второго тестового поста', user_id),
        ('Пост для просмотра', 'Этот пост используется для тестирования просмотра', user_id),
        ('Новый пост', 'Содержание нового поста для тестов', user_id),
    ]
    
    for title, content, author_id in test_posts:
        db.execute(
            'INSERT INTO post (title, content, author_id, created) VALUES (?, ?, ?, datetime("now"))',
            (title, content, author_id)
        )
    db.commit()
    
    # Создаем тестовые комментарии для некоторых постов
    test_comments = [
        (1, user_id, 'Комментарий к первому посту'),  # Комментарий к посту 1
        (1, user_id, 'Второй комментарий к первому посту'),  # Еще один комментарий к посту 1
        (2, user_id, 'Комментарий ко второму посту'),  # Комментарий к посту 2
        (3, user_id, 'Комментарий к третьему посту'),  # Комментарий к посту 3
    ]
    
    for post_id, author_id, content in test_comments:
        db.execute(
            'INSERT INTO comment (post_id, author_id, content, created) VALUES (?, ?, ?, datetime("now"))',
            (post_id, author_id, content)
        )
    db.commit()


@pytest.fixture
def app():
    """Создает тестовое приложение без CSRF защиты для unit тестов."""
    app, db_fd, db_path = _create_test_app({
        'WTF_CSRF_ENABLED': False
    })
    
    yield app
    
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def app_with_csrf():
    """Приложение с включенной CSRF защитой для интеграционных тестов."""
    app, db_fd, db_path = _create_test_app({
        'WTF_CSRF_ENABLED': True
    })
    
    yield app
    
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Тестовый клиент для отправки запросов."""
    return app.test_client()


@pytest.fixture
def auth(client):
    """Фикстура для аутентификации."""
    return AuthActions(client)


@pytest.fixture
def client_with_csrf(app_with_csrf):
    """Клиент с включенной CSRF защитой."""
    return app_with_csrf.test_client()


@pytest.fixture
def auth_with_csrf(client_with_csrf):
    """Аутентификация с CSRF."""
    return AuthActions(client_with_csrf)


@pytest.fixture
def security_app():
    """Приложение для тестов безопасности (CSRF включен)."""
    app, db_fd, db_path = _create_test_app({
        'WTF_CSRF_ENABLED': True,
        'SECRET_KEY': 'security-test-key'
    })
    
    yield app
    
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def security_client(security_app):
    """Клиент для тестов безопасности."""
    return security_app.test_client()


@pytest.fixture
def security_auth(security_client):
    """Аутентификация для тестов безопасности."""
    return AuthActions(security_client)






@pytest.fixture
def runner(app):
    """CLI runner для тестирования команд."""
    return app.test_cli_runner()




class AuthActions:
    """Вспомогательный класс для действий аутентификации в тестах."""

    def __init__(self, client):
        self._client = client

    def _get_full_username(self, username: str) -> str:
        """Получить полное имя пользователя с дискриминатором."""
        if '#' in username:
            return username
            
        # Ищем пользователя в базе данных
        app = self._client.application
        with app.app_context():
            from app.db.db import get_db
            db = get_db()
            cursor = db.execute(
                'SELECT username, discriminator FROM user WHERE username = ?',
                (username,)
            )
            row = cursor.fetchone()
            if row:
                return f"{row[0]}#{row[1]:04d}"
        return username  # fallback, если не найден

    def login(self, username: str = 'test_user#1234', password: str = 'test_pass', follow_redirects: bool = False):
        """Выполнение входа пользователя."""
        # Если username без дискриминатора, пытаемся найти его
        full_username = self._get_full_username(username)
        
        # Получаем CSRF токен если он нужен
        login_data = {'username': full_username, 'password': password}
        
        # Проверяем, включена ли CSRF защита
        app = self._client.application
        if app.config.get('WTF_CSRF_ENABLED', False):
            # Получаем страницу входа чтобы получить CSRF токен
            login_page = self._client.get('/auth/login')
            page_content = login_page.get_data(as_text=True)
            # Ищем CSRF токен в странице
            csrf_match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', page_content, re.DOTALL)
            if csrf_match:
                login_data['csrf_token'] = csrf_match.group(1).strip()
        
        return self._client.post(
            '/auth/login',
            data=login_data,
            follow_redirects=follow_redirects
        )

    def logout(self):
        """Выполнение выхода пользователя."""
        return self._client.get('/auth/logout')

    def register(self, username: str = 'new_user', password: str = 'new_pass123', follow_redirects: bool = False):
        """Регистрация нового пользователя."""
        register_data = {'username': username, 'password': password, 'password2': password}
        
        # Проверяем, включена ли CSRF защита
        app = self._client.application
        if app.config.get('WTF_CSRF_ENABLED', False):
            # Получаем страницу регистрации чтобы получить CSRF токен
            register_page = self._client.get('/auth/register')
            # Ищем CSRF токен в странице
            csrf_match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', register_page.get_data(as_text=True), re.DOTALL)
            if csrf_match:
                register_data['csrf_token'] = csrf_match.group(1).strip()
        
        response = self._client.post(
            '/auth/register',
            data=register_data,
            follow_redirects=follow_redirects
        )
        return response


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


@pytest.fixture
def setup_csrf_token(client):
    """Устанавливает CSRF токен в сессии для тестов."""
    def _setup_token():
        # Получаем страницу входа чтобы извлечь CSRF токен
        login_page = client.get('/auth/login')
        page_content = login_page.get_data(as_text=True)
        csrf_match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', page_content, re.DOTALL)
        if csrf_match:
            return csrf_match.group(1).strip()
        return 'test_csrf_token_for_testing'  # fallback
    return _setup_token


# Маркеры для разных типов тестов
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.security = pytest.mark.security
pytest.mark.database = pytest.mark.database
pytest.mark.slow = pytest.mark.slow

# Описание фикстур:
# - app/client/auth: для unit тестов (CSRF отключен)
# - app_with_csrf/client_with_csrf/auth_with_csrf: для интеграционных тестов (CSRF включен)
# - security_app/security_client/security_auth: для тестов безопасности (CSRF включен)
