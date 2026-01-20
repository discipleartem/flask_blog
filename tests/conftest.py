# tests/conftest.py
import os
import tempfile

import pytest

from app import create_app
from app.db.db import get_db, init_db


@pytest.fixture
def app():
    """Создает тестовое приложение с временной БД."""
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()
        # Создаем тестового пользователя
        db = get_db()
        from app.auth import hash_password
        hashed_pw, _ = hash_password('test_pass')
        db.execute(
            'INSERT INTO user (username, discriminator, password) VALUES (?, ?, ?)',
            ('test_user', 1234, hashed_pw),
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


class AuthActions:
    """Вспомогательный класс для действий аутентификации в тестах."""

    def __init__(self, client):
        self._client = client

    def login(self, username='test_user#1234', password='test_pass', follow_redirects=False):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password},
            follow_redirects=follow_redirects
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)
