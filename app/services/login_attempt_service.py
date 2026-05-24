"""Сервис для отслеживания попыток входа и защиты от bruteforce атаки.

Применяемые паттерны:
- Service — бизнес-логика для защиты от bruteforce
- Rate Limiting — ограничение количества попыток
- Account Lockout — блокировка аккаунта

Применяемые принципы:
- Single Responsibility — только защита от bruteforce
- Fail fast — ранние проверки и блокировки
- KISS — простая и понятная логика
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple

from ..db import execute_query, execute_insert, execute_update


class LoginAttemptService:
    """Сервис для отслеживания попыток входа и защиты от bruteforce атаки."""
    
    def __init__(self):
        """Инициализирует сервис."""
        self.max_attempts = 5  # Максимальное количество неудачных попыток
        self.lockout_duration = timedelta(minutes=15)  # Длительность блокировки
        self.attempt_window = timedelta(minutes=15)  # Окно для подсчета попыток
    
    def record_login_attempt(
        self, 
        ip_address: str, 
        login: str, 
        success: bool
    ) -> bool:
        """Записывает попытку входа в базу данных.
        
        Args:
            ip_address: IP адрес пользователя
            login: Логин пользователя
            success: Успешность попытки входа
            
        Returns:
            True если запись успешна, False при ошибке
        """
        try:
            execute_insert(
                """INSERT INTO login_attempts (ip_address, login, success)
                   VALUES (?, ?, ?)""",
                (ip_address, login, success)
            )
            return True
        except Exception:
            return False
    
    def get_failed_attempts_count(
        self, 
        ip_address: str, 
        login: str
    ) -> int:
        """Возвращает количество неудачных попыток входа за окно времени.
        
        Args:
            ip_address: IP адрес пользователя
            login: Логин пользователя
            
        Returns:
            Количество неудачных попыток
        """
        try:
            cutoff_time = datetime.now() - self.attempt_window
            
            result = execute_query(
                """SELECT COUNT(*) as count FROM login_attempts
                   WHERE ip_address = ? AND login = ? AND success = 0
                   AND attempt_time > ?""",
                (ip_address, login, cutoff_time.isoformat()),
                fetch_all=True
            )
            
            return result[0]['count'] if result else 0
        except Exception:
            return 0
    
    def will_exceed_max_attempts(
        self, 
        ip_address: str, 
        login: str
    ) -> bool:
        """Проверяет, превысит ли текущая попытка максимальное количество.
        
        Args:
            ip_address: IP адрес пользователя
            login: Логин пользователя
            
        Returns:
            True если текущая попытка превысит максимум
        """
        return self.get_failed_attempts_count(ip_address, login) >= self.max_attempts
    
    def is_account_locked(self, user_id: int) -> Tuple[bool, Optional[datetime]]:
        """Проверяет, заблокирован ли аккаунт.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Кортеж (заблокирован, время разблокировки)
        """
        try:
            result = execute_query(
                """SELECT locked_until FROM locked_accounts
                   WHERE user_id = ? AND locked_until > ?""",
                (user_id, datetime.now().isoformat()),
                fetch_all=True
            )
            
            if result:
                locked_until = datetime.fromisoformat(result[0]['locked_until'])
                return True, locked_until
            
            return False, None
        except Exception:
            return False, None
    
    def lock_account(
        self, 
        user_id: int, 
        reason: str = "Too many failed login attempts"
    ) -> bool:
        """Блокирует аккаунт пользователя.
        
        Args:
            user_id: ID пользователя
            reason: Причина блокировки
            
        Returns:
            True если блокировка успешна, False при ошибке
        """
        try:
            locked_until = datetime.now() + self.lockout_duration
            
            execute_insert(
                """INSERT INTO locked_accounts (user_id, locked_until, lock_reason)
                   VALUES (?, ?, ?)""",
                (user_id, locked_until.isoformat(), reason)
            )
            return True
        except Exception:
            return False
    
    def unlock_account(self, user_id: int) -> bool:
        """Разблокирует аккаунт пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            True если разблокировка успешна, False при ошибке
        """
        try:
            execute_update(
                """DELETE FROM locked_accounts WHERE user_id = ?""",
                (user_id,)
            )
            return True
        except Exception:
            return False
    
    def cleanup_old_attempts(self) -> bool:
        """Удаляет старые записи о попытках входа.
        
        Returns:
            True если очистка успешна, False при ошибке
        """
        try:
            cutoff_time = datetime.now() - timedelta(days=7)
            
            execute_update(
                """DELETE FROM login_attempts WHERE attempt_time < ?""",
                (cutoff_time.isoformat(),)
            )
            return True
        except Exception:
            return False
    
    def should_block_login(
        self, 
        ip_address: str, 
        login: str, 
        user_id: Optional[int] = None
    ) -> Tuple[bool, Optional[str]]:
        """Проверяет, следует ли заблокировать попытку входа.
        
        Args:
            ip_address: IP адрес пользователя
            login: Логин пользователя
            user_id: ID пользователя (опционально)
            
        Returns:
            Кортеж (следует_злокировать, причина_блокировки)
        """
        # Проверяем блокировку аккаунта
        if user_id:
            is_locked, locked_until = self.is_account_locked(user_id)
            if is_locked:
                return True, f"Аккаунт заблокирован до {locked_until.strftime('%H:%M')}"
        
        # Проверяем количество неудачных попыток
        failed_attempts = self.get_failed_attempts_count(ip_address, login)
        
        if failed_attempts >= self.max_attempts:
            return True, f"Слишком много неудачных попыток ({failed_attempts})"
        
        return False, None
