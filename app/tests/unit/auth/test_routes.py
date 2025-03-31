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
        # First get the page to obtain CSRF token
        response = client.get('/auth/register')
        html = response.data.decode()
        csrf_token = html.split('csrf_token" type="hidden" value="')[1].split('"')[0]

        # Then post with the token
        response = client.post(
            '/auth/register',
            data={
                'username': 'newuser',
                'password': 'newpassword',
                'csrf_token': csrf_token
            },
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'Registration successful! Please login.' in response.data


    def test_register_validation(self, client, init_database):
        """Test registration input validation"""
        # First get the page to obtain CSRF token
        response = client.get('/auth/register')
        html = response.data.decode()
        csrf_token = html.split('csrf_token" type="hidden" value="')[1].split('"')[0]

        # Test duplicate username
        response = client.post(
            '/auth/register',
            data={
                'username': 'admin',
                'password': 'password',
                'csrf_token': csrf_token
            },
            follow_redirects=True
        )
        assert b'Username already taken' in response.data

        # Test empty username
        response = client.post(
            '/auth/register',
            data={
                'username': '',
                'password': 'test123',
                'csrf_token': csrf_token
            }
        )
        assert b'Username is required.' in response.data

        # Test empty password
        response = client.post(
            '/auth/register',
            data={
                'username': 'test2',
                'password': '',
                'csrf_token': csrf_token
            }
        )
        assert b'Password is required.' in response.data



    def test_login_success(self, client, init_database):
        """Test successful login"""
        # First get the login page to obtain CSRF token
        response = client.get('/auth/login')
        html = response.data.decode()
        csrf_token = html.split('csrf_token" type="hidden" value="')[1].split('"')[0]

        # Then post with the token
        response = client.post(
            '/auth/login',
            data={
                'username': 'admin',
                'password': 'qwerty',
                'csrf_token': csrf_token
            },
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
        # First get the login page to obtain CSRF token
        response = client.get('/auth/login')
        html = response.data.decode()
        csrf_token = html.split('csrf_token" type="hidden" value="')[1].split('"')[0]

        # Then post with the token
        response = client.post(
            '/auth/login',
            data={
                'username': 'admin',
                'password': 'wrong_password',
                'csrf_token': csrf_token
            },
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data



    def test_logout(self, client, init_database):
        """Test logout functionality"""
        # First login
        response = client.get('/auth/login')
        html = response.data.decode()
        csrf_token = html.split('csrf_token" type="hidden" value="')[1].split('"')[0]

        response = client.post(
            '/auth/login',
            data={
                'username': 'admin',
                'password': 'qwerty',
                'csrf_token': csrf_token
            },
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'Successfully logged in' in response.data

        # Then test logout
        response = client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'Successfully logged out' in response.data

        with client:
            assert '_user_id' not in session