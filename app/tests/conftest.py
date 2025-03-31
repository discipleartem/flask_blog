import os
import tempfile
import pytest
from app import create_app
from app.db import init_db, get_db
from app.models.user import User

@pytest.fixture
def app():
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp()

    # Configure app for testing
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
        'SECRET_KEY': 'test_secret_key',
        'WTF_CSRF_ENABLED': False
    })

    # Initialize database schema
    with app.app_context():
        init_db()

    yield app

    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def init_database(app):
    with app.app_context():
        # Setup test database with initial data
        User.create_user('admin', 'qwerty')
        db = get_db()
        # Add test user with hashed password
        db.execute(
            'INSERT INTO users (username, password_hash) VALUES (?, ?)',
            ('test', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f')
        )
        db.commit()
        yield

@pytest.fixture
def login_user(client):
    client.post('/auth/login',
        data={'username': 'admin', 'password': 'qwerty'},
        follow_redirects=True
    )
    yield
    client.get('/auth/logout', follow_redirects=True)