"""JWT сервис для самописной авторизации.

Применяемые паттерны:
- Service Layer — инкапсулирует логику работы с JWT
- Singleton — один экземпляр для всего приложения
- Strategy — жестко закодированный алгоритм безопасности

Применяемые принципы:
- Single Responsibility — только работа с JWT токенами
- Explicit is better than implicit — явные методы
- Security first — безопасная реализация JWT
"""

import base64
import hashlib
import hmac
import json
import time
from typing import Optional, TypedDict

from flask import current_app


class Payload(TypedDict):
    """Структура payload для JWT токена."""
    user_id: int
    exp: int
    iat: int


class JWTService:
    """Сервис для работы с JWT токенами.
    
    Реализует самописный JWT без хранения алгоритма в токене
    для повышения безопасности.
    """
    
    # Жестко закодированный алгоритм (не храним в токене!)
    ALGORITHM = "HS256"
    
    # Сопоставление алгоритмов с функциями хэширования
    ALGORITHMS = {
        "HS256": hashlib.sha256,
        "HS384": hashlib.sha384,
        "HS512": hashlib.sha512
    }
    
    def __init__(self):
        """Инициализирует JWT сервис."""
        pass
    
    def generate_token(self, user_id: int, remember_me: bool = False) -> str:
        """Генерирует JWT токен для пользователя.
        
        Args:
            user_id: ID пользователя
            remember_me: Запомнить на 30 дней вместо 24 часов
            
        Returns:
            JWT токен в формате payload.signature
        """
        exp_hours = 720 if remember_me else 24  # 30*24=720 или 24 часа
        encoded_payload = self._create_payload(user_id, exp_hours)
        encoded_signature = self._create_signature(encoded_payload)
        token = f"{encoded_payload}.{encoded_signature}"
        return token
    
    def verify_token(self, token: str) -> Optional[Payload]:
        """Проверяет и декодирует JWT токен.
        
        Args:
            token: JWT токен
            
        Returns:
            Payload токена или None если токен невалиден
        """
        parts = token.split('.')
        if len(parts) != 2:
            return None
        
        payload, signature = parts[0], parts[1]
        
        # Проверяем подпись
        expected_signature = self._create_signature(payload)
        if not hmac.compare_digest(signature, expected_signature):
            return None
        
        # Проверяем срок действия
        current_time = int(time.time())
        
        try:
            # Декодируем payload
            payload_json = base64.urlsafe_b64decode(
                self._add_padding(payload)
            ).decode('utf-8')
            payload_data = json.loads(payload_json)
            exp_time = payload_data.get('exp', 0)
        except Exception:
            return None
        
        if current_time > exp_time:
            return None
        
        return payload_data
    
    def _create_payload(self, user_id: int, exp_hours: int) -> str:
        """Создает закодированный payload.
        
        Args:
            user_id: ID пользователя
            exp_hours: Срок действия в часах
            
        Returns:
            Закодированный payload
        """
        current_time = int(time.time())  # Unix timestamp
        exp_time = current_time + (exp_hours * 3600)  # 3600 секунд = 1 час
        
        payload_data = {
            "user_id": user_id,
            "exp": exp_time,  # дата истечения
            "iat": current_time  # дата создания
        }
        
        # Сериализуем в JSON
        payload_json = json.dumps(payload_data, separators=(',', ':'))
        
        # Кодируем в base64 без padding
        encoded_payload = base64.urlsafe_b64encode(
            payload_json.encode('utf-8')
        ).decode('utf-8').rstrip('=')
        
        return encoded_payload
    
    def _create_signature(self, payload: str) -> str:
        """Создает подпись для payload.
        
        Args:
            payload: Закодированный payload
            
        Returns:
            Закодированная подпись
        """
        secret_key = current_app.config.get('SECRET_KEY', 'default-secret')
        
        signature = hmac.new(
            secret_key.encode('utf-8'),
            payload.encode('utf-8'),
            self.ALGORITHMS[self.ALGORITHM]
        ).digest()
        
        # Кодируем в base64 без padding
        encoded_signature = base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')
        return encoded_signature
    
    def _add_padding(self, encoded_string: str) -> str:
        """Добавляет padding для base64 строки.
        
        Args:
            encoded_string: Base64 строка без padding
            
        Returns:
            Base64 строка с padding
        """
        padding_needed = 4 - (len(encoded_string) % 4)
        if padding_needed:
            encoded_string += '=' * padding_needed
        return encoded_string
