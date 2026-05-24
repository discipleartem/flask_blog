"""Константы ролей системы.

Применяемые паттерны:
- Constants — централизованное хранение констант
- Single Source of Truth — единый источник правды для ролей

Применяемые принципы:
- DRY (Don't Repeat Yourself) — избегаем дублирования
- Explicit is better than implicit — явные константы
"""

from enum import Enum
from typing import Final


class SystemRole(str, Enum):
    """Системные роли пользователей."""
    ADMIN: Final = "admin"
    COMMON: Final = "common"


# Список всех базовых ролей для миграций
BASE_ROLES: Final = [
    (SystemRole.ADMIN, "Полный доступ к системе"),
    (SystemRole.COMMON, "Базовый пользователь"),
]


def get_all_role_names() -> list[str]:
    """Возвращает список всех названий ролей."""
    return [role.value for role in SystemRole]


def is_valid_role(role_name: str) -> bool:
    """Проверяет, является ли роль валидной.
    
    Args:
        role_name: Название роли для проверки
        
    Returns:
        True если роль существует в системе
    """
    return role_name in get_all_role_names()
