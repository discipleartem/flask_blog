"""Модель данных для пользователей.

Применяемые паттерны:
- Data Transfer Object (DTO) — контейнер для данных пользователя
- Immutable Object — объект не изменяется после создания

Применяемые принципы:
- Type safety — строгие типы данных
- Explicit is better than implicit — явные поля
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from app.constants.roles import SystemRole


@dataclass
class User:
    """Модель пользователя блога.
    
    Содержит основную информацию о пользователе.
    Роли определяются через связи many-to-many с таблицей roles.
    """
    id: int
    login: str
    discriminator: Optional[str]
    password_hash: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    # Дополнительные поля из JOIN запросов
    _roles: Optional[list[str]] = None  # Список ролей пользователя

    @property
    def login_full(self) -> str:
        """Возвращает login#discriminator для отображения."""
        if self.login == 'admin' and self.discriminator == '0000':
            return 'admin'
        return f"{self.login}#{self.discriminator}"
    
    @property
    def is_common(self) -> bool:
        """Проверяет, является ли пользователь обычным (не admin)."""
        return not (self.login == 'admin' and self.discriminator == '0000')
    
    @property
    def roles(self) -> list[str]:
        """Возвращает список ролей пользователя."""
        return self._roles or []
    
    @property
    def is_admin(self) -> bool:
        """Проверяет, имеет ли пользователь роль admin."""
        return SystemRole.ADMIN in self.roles
    
    @property
    def has_role(self, role_name: str) -> bool:
        """Проверяет, имеет ли пользователь указанную роль.
        
        Args:
            role_name: Название роли (рекомендуется использовать SystemRole)
            
        Returns:
            True если пользователь имеет указанную роль
        """
        return role_name in self.roles
    
    @property
    def created_date_formatted(self) -> str:
        """Возвращает отформатированную дату регистрации."""
        return self.created_at.strftime('%d.%m.%Y %H:%M')
    
    @classmethod
    def create_new(cls, id: int, login: str, discriminator: Optional[str], password_hash: str, initial_roles: Optional[list[str]] = None) -> 'User':
        """Создает нового пользователя с ролью по умолчанию.
        
        Args:
            id: ID пользователя
            login: Логин пользователя
            discriminator: Дискриминатор ("0000" для admin или 4 цифры для обычных)
            password_hash: Хеш пароля
            initial_roles: Начальные роли пользователя (опционально)
            
        Returns:
            Новый пользователь с ролью по умолчанию
        """
        # Для admin всегда используем "0000"
        if login == 'admin':
            discriminator = '0000'
        elif discriminator is None:
            discriminator = '0000'  # fallback
            
        user = cls(
            id=id,
            login=login,
            discriminator=discriminator,
            password_hash=password_hash
        )
        # Устанавливаем роль по умолчанию или переданные роли
        user._roles = initial_roles or ['user']
        return user