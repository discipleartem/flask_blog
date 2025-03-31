import pytest
from flask import session, g

@pytest.mark.auth
class TestAuthRoutes:
    def test_login_get(self, client):
        """Test GET request to login page"""
        response = client.get('/auth/login')
        assert response.status_code == 200

    def test_register_get(self, client):
        """Test GET request to register page"""
        response = client.get('/auth/register')
        assert response.status_code == 200

    def test_register_success(self, client, app, init_database):
        """Test successful registration"""
        response = client.post(
            '/auth/register',
            data={'username': 'newuser', 'password': 'newpassword'},
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'Registration successful! Please login.' in response.data

        # Verify database entry
        with app.app_context():
            from app.db import get_db
            db = get_db()
            user = db.execute(
                "SELECT * FROM users WHERE username = 'newuser'"
            ).fetchone()
            assert user is not None

    def test_register_validation(self, client, init_database):
        """Test registration input validation"""
        # Test duplicate username
        response = client.post(
            '/auth/register',
            data={'username': 'admin', 'password': 'password'},
            follow_redirects=True
        )
        assert b'Username already taken' in response.data

        # Test empty username
        response = client.post(
            '/auth/register',
            data={'username': '', 'password': 'test123'}
        )
        assert b'Username is required.' in response.data

        # Test empty password
        response = client.post(
            '/auth/register',
            data={'username': 'test2', 'password': ''}
        )
        assert b'Password is required.' in response.data

    def test_login_success(self, client, init_database):
        """Test successful login"""
        response = client.post('/auth/login',
                               data={'username': 'admin', 'password': 'qwerty'},
                               follow_redirects=True
                               )
        assert response.status_code == 200
        assert b'Successfully logged in' in response.data

        with client:
            client.get('/')
            assert session['_user_id'] is not None
            assert g.user is not None

    def test_login_invalid(self, client, init_database):
        """Test login with invalid credentials"""
        response = client.post('/auth/login',
                               data={'username': 'admin', 'password': 'wrong_password'},
                               follow_redirects=True
                               )
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data

    def test_logout(self, client, init_database, login_user):
        """Test logout functionality"""
        response = client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'Successfully logged out' in response.data

        with client:
            assert '_user_id' not in session