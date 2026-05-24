"""Модель данных для комментариев.

Применяемые паттерны:
- Data Transfer Object (DTO) — контейнер для данных комментария
- Immutable Object — объект не изменяется после создания

Применяемые принципы:
- Type safety — строгие типы данных
- Explicit is better than implicit — явные поля
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Comment:
    """Модель комментария к посту.
    
    Содержит информацию о комментарии включая автора и пост.
    """
    id: int
    post_id: int
    user_id: int
    body: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    # Дополнительные поля из JOIN запросов
    author_login: Optional[str] = None
    author_discriminator: Optional[str] = None
    author_roles: Optional[list[str]] = None
    post_title: Optional[str] = None

    @property
    def author_display_name(self) -> str:
        """Возвращает отображаемое имя автора."""
        if self.author_login == 'admin':
            return 'admin'
        return f"{self.author_login}#{self.author_discriminator}"
    
    @property
    def author_is_admin(self) -> bool:
        """Проверяет, является ли автор администратором."""
        return self.author_roles and 'admin' in self.author_roles
    
    @property
    def created_date_formatted(self) -> str:
        """Возвращает отформатированную дату создания."""
        return self.created_at.strftime('%d.%m.%Y %H:%M')
    
    @property
    def is_edited(self) -> bool:
        """Проверяет, был ли комментарий отредактирован."""
        if not self.updated_at:
            return False
        return abs((self.updated_at - self.created_at).total_seconds()) > 1