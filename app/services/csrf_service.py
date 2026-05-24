"""CSRF защита для форм.

Применяемые паттерны:
- Security — защита от CSRF атак
- Service — инкапсуляция логики CSRF
- Singleton — один экземпляр для приложения

Применяемые принципы:
- Secure by default — защита включена по умолчанию
- Explicit is better than implicit — явная генерация токенов
- Fail fast — ранние проверки безопасности
"""

import hashlib
import hmac
import secrets
from typing import Optional

from flask import current_app, session


class CSRFService:
    """Сервис для CSRF защиты форм."""
    
    def __init__(self, secret_key: str):
        """Инициализация CSRF сервиса.
        
        Args:
            secret_key: Секретный ключ для подписи токенов
        """
        self.secret_key = secret_key.encode()
    
    def generate_token(self) -> str:
        """Генерирует новый CSRF токен.
        
        Returns:
            CSRF токен для использования в формах
        """
        # Генерируем случайную строку
        random_data = secrets.token_urlsafe(32)
        
        # Создаем подпись
        signature = hmac.new(
            self.secret_key,
            random_data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Сохраняем токен в сессии
        session['csrf_token'] = f"{random_data}.{signature}"
        
        return session['csrf_token']
    
    def verify_token(self, token: str) -> bool:
        """Проверяет валидность CSRF токена.
        
        Args:
            token: CSRF токен из формы
            
        Returns:
            True если токен валиден, иначе False
        """
        if not token:
            return False
        
        # Получаем сохраненный токен из сессии
        stored_token = session.get('csrf_token')
        if not stored_token:
            return False
        
        # Проверяем совпадение токенов
        if not hmac.compare_digest(token, stored_token):
            return False
        
        # Дополнительно проверяем подпись
        try:
            random_data, expected_signature = token.split('.', 1)
            
            # Пересчитываем подпись
            actual_signature = hmac.new(
                self.secret_key,
                random_data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, actual_signature)
            
        except (ValueError, IndexError):
            return False
    
    def get_token(self) -> str:
        """Возвращает текущий CSRF токен или генерирует новый.
        
        Returns:
            CSRF токен
        """
        if 'csrf_token' not in session:
            return self.generate_token()
        
        return session['csrf_token']
    
    def clear_token(self) -> None:
        """Удаляет CSRF токен из сессии."""
        session.pop('csrf_token', None)
    
    def validate_request(self) -> bool:
        """Проверяет CSRF токен из текущего запроса.
        
        Returns:
            True если токен валиден, иначе False
        """
        from flask import request
        
        # Пропускаем безопасные методы
        if request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            return True
        
        # Получаем токен из формы или заголовка
        token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
        
        return self.verify_token(token)


def get_csrf_service() -> CSRFService:
    """Возвращает экземпляр CSRF сервиса.
    
    Returns:
        CSRFService: Экземпляр сервиса
    """
    return current_app.csrf_service


def generate_csrf_token() -> str:
    """Генерирует CSRF токен для использования в шаблонах.
    
    Returns:
        CSRF токен
    """
    return get_csrf_service().get_token()


def validate_csrf_token(token: str) -> bool:
    """Проверяет валидность CSRF токена.
    
    Args:
        token: CSRF токен для проверки
        
    Returns:
        True если токен валиден, иначе False
    """
    return get_csrf_service().verify_token(token)