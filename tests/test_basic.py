"""Базовые тесты для MVP функциональности Flask Blog.

Применяемые паттерны:
- Test Fixture — подготовка тестового окружения
- Arrange-Act-Assert — структура тестов
- Test Pyramid — разные уровни тестирования

Применяемые принципы:
- Test Isolation — независимые тесты
- Explicit Testing — явные проверки
- Fail Fast — быстрые тесты
"""

import os
import tempfile
import unittest
from typing import Any

from app import create_app
from app.config import Config


class TestConfig(Config):
    """Тестовая конфигурация."""
    TESTING = True
    SECRET_KEY = 'test-secret-key'
    DATABASE_URL = 'sqlite:///:memory:'  # В памяти для тестов
    WTF_CSRF_ENABLED = False  # Отключаем CSRF для тестов


class BaseTestCase(unittest.TestCase):
    """Базовый класс для всех тестов."""
    
    def setUp(self) -> None:
        """Подготовка тестового окружения."""
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Инициализируем БД
        from app import db
        db.init_db()
        
        # Создаем админа для тестов
        with self.app.test_request_context():
            from app.services import UserAuthService
            auth_service = self.app.auth_service
            
            # Регистрируем админа
            success, message, user = auth_service.register_user('admin', 'admin123')
            if success:
                # Назначаем роль админа
                from app.repositories import UserRepository
                user_repo = UserRepository()
                user_repo.assign_role(user.id, 'admin')
    
    def tearDown(self) -> None:
        """Очистка после тестов."""
        self.app_context.pop()


class TestAuth(BaseTestCase):
    """Тесты авторизации."""
    
    def test_register_user_success(self) -> None:
        """Тест успешной регистрации пользователя."""
        response = self.client.post('/auth/register', data={
            'login': 'testuser',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        })
        
        # Проверяем редирект на главную страницу
        self.assertEqual(response.status_code, 302)
        
        # Проверяем, что пользователь создан
        from app.repositories import UserRepository
        user_repo = UserRepository()
        users = user_repo.find_by_login('testuser')
        self.assertEqual(len(users), 1)
    
    def test_register_user_passwords_not_match(self) -> None:
        """Тест регистрации с несовпадающими паролями."""
        response = self.client.post('/auth/register', data={
            'login': 'testuser',
            'password': 'testpass123',
            'password_confirm': 'differentpass'
        })
        
        # Должна остаться на странице регистрации с ошибкой
        self.assertEqual(response.status_code, 200)
        self.assertIn('Пароли не совпадают', response.get_data(as_text=True))
    
    def test_login_admin_success(self) -> None:
        """Тест успешного входа админа."""
        response = self.client.post('/auth/login', data={
            'login': 'admin',
            'password': 'admin123'
        })
        
        # Проверяем редирект на главную страницу
        self.assertEqual(response.status_code, 302)
        
        # Проверяем наличие JWT токена в cookies
        self.assertIn('auth_token', response.headers.get('Set-Cookie', ''))
    
    def test_login_invalid_credentials(self) -> None:
        """Тест входа с неверными данными."""
        response = self.client.post('/auth/login', data={
            'login': 'admin',
            'password': 'wrongpassword'
        })
        
        # Должна остаться на странице входа с ошибкой
        self.assertEqual(response.status_code, 200)
        self.assertIn('Неверный', response.get_data(as_text=True))
    
    def test_logout(self) -> None:
        """Тест выхода."""
        # Сначала входим
        self.client.post('/auth/login', data={
            'login': 'admin',
            'password': 'admin123'
        })
        
        # Затем выходим
        response = self.client.get('/auth/logout')
        
        # Проверяем редирект на страницу входа
        self.assertEqual(response.status_code, 302)
        
        # Проверяем, что токен удален
        self.assertIn('auth_token=;', response.headers.get('Set-Cookie', ''))


class TestBlog(BaseTestCase):
    """Тесты функциональности блога."""
    
    def setUp(self) -> None:
        """Расширенная подготовка для тестов блога."""
        super().setUp()
        
        # Создаем тестового пользователя
        with self.app.test_request_context():
            from app.services import UserAuthService
            auth_service = self.app.auth_service
            
            success, message, self.user = auth_service.register_user('bloguser', 'blogpass123')
            
            # Входим и получаем токен
            success, message, self.token = auth_service.login_user('bloguser', 'blogpass123')
    
    def test_create_post_success(self) -> None:
        """Тест успешного создания поста."""
        # Устанавливаем токен в cookies
        self.client.set_cookie('auth_token', self.token)
        
        response = self.client.post('/blog/create', data={
            'title': 'Test Post Title',
            'body': 'This is a test post content.'
        })
        
        # Проверяем редирект на главную страницу
        self.assertEqual(response.status_code, 302)
        
        # Проверяем, что пост создан
        from app.repositories import PostRepository
        post_repo = PostRepository()
        posts = post_repo.get_all()
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0].title, 'Test Post Title')
    
    def test_create_post_unauthorized(self) -> None:
        """Тест создания поста без авторизации."""
        response = self.client.post('/blog/create', data={
            'title': 'Test Post Title',
            'body': 'This is a test post content.'
        })
        
        # Должен быть редирект на страницу входа
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response.location)
    
    def test_index_page(self) -> None:
        """Тест главной страницы."""
        response = self.client.get('/blog/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Flask Blog', response.get_data(as_text=True))
    
    def test_post_detail(self) -> None:
        """Тест детальной страницы поста."""
        # Сначала создаем пост
        with self.app.test_request_context():
            from app.repositories import PostRepository
            post_repo = PostRepository()
            post_id = post_repo.create({
                'user_id': self.user.id,
                'title': 'Test Post',
                'body': 'Test content'
            })
        
        # Проверяем страницу поста
        response = self.client.get(f'/blog/post/{post_id}')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test Post', response.get_data(as_text=True))
        self.assertIn('Test content', response.get_data(as_text=True))


class TestCSRF(BaseTestCase):
    """Тесты CSRF защиты."""
    
    def test_csrf_token_generation(self) -> None:
        """Тест генерации CSRF токена."""
        with self.app.test_request_context():
            from app.services.csrf_service import generate_csrf_token
            
            token = generate_csrf_token()
            
            # Проверяем, что токен не пустой
            self.assertIsNotNone(token)
            self.assertGreater(len(token), 10)
            
            # Проверяем, что токен сохраняется в сессии
            self.assertIn('csrf_token', token)
    
    def test_csrf_token_verification(self) -> None:
        """Тест проверки CSRF токена."""
        with self.app.test_request_context():
            from app.services.csrf_service import get_csrf_service
            
            csrf_service = get_csrf_service()
            
            # Генерируем токен
            token = csrf_service.generate_token()
            
            # Проверяем валидный токен
            self.assertTrue(csrf_service.verify_token(token))
            
            # Проверяем невалидный токен
            self.assertFalse(csrf_service.verify_token('invalid-token'))
            
            # Проверяем пустой токен
            self.assertFalse(csrf_service.verify_token(''))


class TestJWT(BaseTestCase):
    """Тесты JWT сервиса."""
    
    def test_jwt_generation_and_verification(self) -> None:
        """Тест генерации и проверки JWT токена."""
        with self.app.test_request_context():
            from app.services import JWTService
            
            jwt_service = JWTService()
            
            # Генерируем токен
            token = jwt_service.generate_token(1)
            
            # Проверяем, что токен не пустой
            self.assertIsNotNone(token)
            self.assertGreater(len(token), 20)
            
            # Проверяем валидацию токена
            payload = jwt_service.verify_token(token)
            
            self.assertIsNotNone(payload)
            self.assertEqual(payload['user_id'], 1)
            self.assertIn('exp', payload)
            self.assertIn('iat', payload)
    
    def test_jwt_invalid_token(self) -> None:
        """Тест проверки невалидного JWT токена."""
        with self.app.test_request_context():
            from app.services import JWTService
            
            jwt_service = JWTService()
            
            # Проверяем невалидный токен
            payload = jwt_service.verify_token('invalid.jwt.token')
            
            self.assertIsNone(payload)


if __name__ == '__main__':
    unittest.main()