"""Репозиторий для работы с пользователями.

Применяемые паттерны:
- Repository (Хранилище) — инкапсулирует логику доступа к данным
- Data Mapper — преобразование строк БД в объекты

Применяемые принципы:
- Single Responsibility — только работа с пользователями
- Explicit is better than implicit — явные SQL запросы
- Type safety — строгие типы возвращаемых значений
"""

from datetime import datetime
from typing import List, Optional

from ..db import execute_insert, execute_query, execute_update
from ..models.users import User
from ..constants.roles import SystemRole


class UserRepository:
    """Репозиторий для доступа к данным пользователей.
    
    Предоставляет методы для CRUD операций с пользователями,
    включая работу с ролями и дискриминаторами.
    """
    
    def find_by_id(self, user_id: int) -> Optional[User]:
        """Находит пользователя по ID с ролями.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Объект User или None если не найден
        """
        query = """
        SELECT u.id, u.login, u.discriminator, u.password_hash, 
               u.created_at, u.updated_at,
               GROUP_CONCAT(r.name) as roles
        FROM users u
        LEFT JOIN user_roles ur ON u.id = ur.user_id
        LEFT JOIN roles r ON ur.role_id = r.id
        WHERE u.id = ?
        GROUP BY u.id
        """
        result = execute_query(query, (user_id,), fetch_one=True)
        
        if result:
            roles = result['roles'].split(',') if result['roles'] else []
            return User(
                id=result['id'],
                login=result['login'],
                discriminator=result['discriminator'],
                password_hash=result['password_hash'],
                created_at=result['created_at'],
                updated_at=result['updated_at'],
                _roles=roles
            )
        return None
    
    def find_by_login_and_discriminator(self, login: str, discriminator: str) -> Optional[User]:
        """Находит пользователя по логину и дискриминатору с ролями.
        
        Args:
            login: Логин пользователя
            discriminator: Дискриминатор (4 цифры)
            
        Returns:
            Объект User или None если не найден
        """
        query = """
        SELECT u.id, u.login, u.discriminator, u.password_hash,
               u.created_at, u.updated_at,
               GROUP_CONCAT(r.name) as roles
        FROM users u
        LEFT JOIN user_roles ur ON u.id = ur.user_id
        LEFT JOIN roles r ON ur.role_id = r.id
        WHERE u.login = ? AND u.discriminator = ?
        GROUP BY u.id
        """
        result = execute_query(query, (login, discriminator), fetch_one=True)
        
        if result:
            roles = result['roles'].split(',') if result['roles'] else []
            return User(
                id=result['id'],
                login=result['login'],
                discriminator=result['discriminator'],
                password_hash=result['password_hash'],
                created_at=result['created_at'],
                updated_at=result['updated_at'],
                _roles=roles
            )
        return None
    
    def find_by_login(self, login: str) -> List[User]:
        """Находит всех пользователей с указанным логином с ролями.
        
        Args:
            login: Логин пользователя
            
        Returns:
            Список пользователей с указанным логином
        """
        query = """
        SELECT u.id, u.login, u.discriminator, u.password_hash,
               u.created_at, u.updated_at,
               GROUP_CONCAT(r.name) as roles
        FROM users u
        LEFT JOIN user_roles ur ON u.id = ur.user_id
        LEFT JOIN roles r ON ur.role_id = r.id
        WHERE u.login = ?
        GROUP BY u.id
        ORDER BY u.discriminator
        """
        results = execute_query(query, (login,), fetch_all=True)
        
        users = []
        for result in results:
            roles = result['roles'].split(',') if result['roles'] else []
            users.append(User(
                id=result['id'],
                login=result['login'],
                discriminator=result['discriminator'],
                password_hash=result['password_hash'],
                created_at=result['created_at'],
                updated_at=result['updated_at'],
                _roles=roles
            ))
        return users
    
    def find_admin(self) -> Optional[User]:
        """Находит администратора системы.
        
        Returns:
            Объект User для администратора или None
        """
        query = """
        SELECT u.id, u.login, u.discriminator, u.password_hash,
               u.created_at, u.updated_at,
               GROUP_CONCAT(r.name) as roles
        FROM users u
        JOIN user_roles ur ON u.id = ur.user_id
        JOIN roles r ON ur.role_id = r.id
        WHERE u.login = ? AND r.name = ?
        GROUP BY u.id
        LIMIT 1
        """
        result = execute_query(query, (SystemRole.ADMIN, SystemRole.ADMIN), fetch_one=True)
        
        if result:
            roles = result['roles'].split(',') if result['roles'] else []
            return User(
                id=result['id'],
                login=result['login'],
                discriminator=result['discriminator'],
                password_hash=result['password_hash'],
                created_at=result['created_at'],
                updated_at=result['updated_at'],
                _roles=roles
            )
        return None
    
    def is_login_reserved(self, login: str) -> bool:
        """Проверяет, зарезервирован ли логин.
        
        Args:
            login: Логин для проверки
            
        Returns:
            True если логин зарезервирован
        """
        reserved_logins = [SystemRole.ADMIN]
        return login.lower() in reserved_logins
    
    def is_discriminator_available(self, login: str, discriminator: str) -> bool:
        """Проверяет, доступен ли дискриминатор для указанного логина.
        
        Args:
            login: Логин пользователя
            discriminator: Дискриминатор для проверки
            
        Returns:
            True если дискриминатор доступен
        """
        existing = self.find_by_login_and_discriminator(login, discriminator)
        return existing is None
    
    def generate_discriminator(self, login: str) -> str:
        """Генерирует случайный дискриминатор для логина.
        
        Args:
            login: Логин пользователя
            
        Returns:
            Уникальный дискриминатор (4 цифры)
            
        Raises:
            ValueError: если логин зарезервирован или не удалось сгенерировать дискриминатор
        """
        import random
        
        # Запрещаем генерировать дискриминаторы для зарезервированных логинов
        if self.is_login_reserved(login):
            raise ValueError("Логин зарезервирован системой")
        
        max_attempts = 100
        for _ in range(max_attempts):
            discriminator = f"{random.randint(1, 9999):04d}"
            if self.is_discriminator_available(login, discriminator):
                return discriminator
        
        raise ValueError("Не удалось сгенерировать уникальный дискриминатор")
    
    def create_user(self, login: str, password_hash: str, discriminator: Optional[str] = None) -> int:
        """Создает нового пользователя с ролью по умолчанию.
        
        Args:
            login: Логин пользователя
            password_hash: Хэш пароля
            discriminator: Дискриминатор (None для auto-generate)
            
        Returns:
            ID созданного пользователя
        """
        if discriminator is None and not self.is_login_reserved(login):
            discriminator = self.generate_discriminator(login)
        
        query = """
        INSERT INTO users (login, discriminator, password_hash, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        """
        now = datetime.utcnow()
        user_id = execute_insert(
            query, 
            (login, discriminator, password_hash, now, now)
        )
        
        # Назначаем роль по умолчанию
        default_role = 'user'  # Роль по умолчанию
        self.assign_role(user_id, default_role)
        
        return user_id
    
    def assign_role(self, user_id: int, role_name: str) -> bool:
        """Назначает роль пользователю.
        
        Args:
            user_id: ID пользователя
            role_name: Название роли
            
        Returns:
            True если роль назначена успешно
        """
        query = """
        INSERT OR IGNORE INTO user_roles (user_id, role_id)
        VALUES (?, (SELECT id FROM roles WHERE name = ?))
        """
        affected_rows = execute_update(query, (user_id, role_name))
        return affected_rows > 0
    
    def update_password(self, user_id: int, password_hash: str) -> bool:
        """Обновляет пароль пользователя.
        
        Args:
            user_id: ID пользователя
            password_hash: Новый хэш пароля
            
        Returns:
            True если пароль обновлен
        """
        query = """
        UPDATE users SET password_hash = ?, updated_at = ?
        WHERE id = ?
        """
        affected_rows = execute_update(
            query, 
            (password_hash, datetime.utcnow(), user_id)
        )
        return affected_rows > 0
    
    def delete_user(self, user_id: int) -> bool:
        """Удаляет пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            True если пользователь удален
        """
        # Сначала удаляем связи с ролями
        execute_update("DELETE FROM user_roles WHERE user_id = ?", (user_id,))
        
        # Затем удаляем пользователя
        query = "DELETE FROM users WHERE id = ?"
        affected_rows = execute_update(query, (user_id,))
        return affected_rows > 0