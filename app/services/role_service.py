"""Сервис для управления ролями пользователей.

Применяемые паттерны:
- Service Layer — инкапсуляция бизнес-логики управления ролями
- Dependency Injection — зависимости передаются через конструктор

Применяемые принципы:
- Single Responsibility — одна ответственность за управление ролями
- Explicit dependencies — явные зависимости
"""

from typing import Optional

from app.constants.roles import SystemRole, BASE_ROLES, is_valid_role


class RoleService:
    """Сервис для управления ролями пользователей."""
    
    @staticmethod
    def get_default_role() -> str:
        """Возвращает роль по умолчанию для новых пользователей.
        
        Returns:
            Название роли по умолчанию
        """
        return SystemRole.COMMON
    
    @staticmethod
    def get_base_roles() -> list[tuple[str, str]]:
        """Возвращает список базовых ролей для инициализации.
        
        Returns:
            Список кортежей (название_роли, описание)
        """
        return BASE_ROLES.copy()
    
    @staticmethod
    def is_role_valid(role_name: str) -> bool:
        """Проверяет, является ли роль валидной.
        
        Args:
            role_name: Название роли для проверки
            
        Returns:
            True если роль существует в системе
        """
        return is_valid_role(role_name)
    
    @staticmethod
    def get_user_initial_roles() -> list[str]:
        """Возвращает список ролей для нового пользователя при регистрации.
        
        Returns:
            Список ролей для присвоения новому пользователю
        """
        return [RoleService.get_default_role()]
    
    @staticmethod
    def can_user_have_role(user_role: str, target_role: str) -> bool:
        """Проверяет, может ли пользователь с указанной ролью получить целевую роль.
        
        Args:
            user_role: Текущая роль пользователя
            target_role: Целевая роль для проверки
            
        Returns:
            True если пользователь может получить целевую роль
        """
        # Базовая логика: admin может получить любую роль
        if user_role == SystemRole.ADMIN:
            return RoleService.is_role_valid(target_role)
        
        # Обычный пользователь может получить только common роль
        return target_role == SystemRole.COMMON
