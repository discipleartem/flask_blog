"""Сервис для авторизации пользователей.

Применяемые паттерны:
- Service Layer — инкапсулирует бизнес-логику авторизации
- Dependency Injection — внедрение репозиториев
- Strategy — разные стратегии для обычных пользователей и admin

Применяемые принципы:
- Single Responsibility — только авторизация и регистрация
- Explicit is better than implicit — явная логика
- Fail fast — ранние проверки и ошибки
"""

from typing import Optional, Tuple

from werkzeug.security import check_password_hash, generate_password_hash

from ..models.users import User
from ..repositories.user_repo import UserRepository
from .jwt_service import JWTService


class UserAuthService:
    """Сервис для авторизации пользователей.
    
    Обеспечивает регистрацию, вход и управление пользователями
    с системой логин + дискриминатор (в стиле Discord).
    """
    
    def __init__(self, user_repo: UserRepository, jwt_service: JWTService):
        """Инициализирует сервис с зависимостями.
        
        Args:
            user_repo: Репозиторий пользователей
            jwt_service: Сервис для работы с JWT токенами
        """
        self.user_repo = user_repo
        self.jwt_service = jwt_service
    
    def register_user(self, login: str, password: str) -> Tuple[bool, str, Optional[User]]:
        """Регистрирует нового пользователя.
        
        Args:
            login: Логин пользователя
            password: Пароль пользователя
            
        Returns:
            Кортеж (успех, сообщение, пользователь)
        """
        
        # Проверяем зарезервированные логины
        if self.user_repo.is_login_reserved(login):
            return False, "Логин зарезервирован системой", None
        
        # Проверяем длину логина
        if len(login) < 3 or len(login) > 32:
            return False, "Логин должен быть от 3 до 32 символов", None
        
        # Проверяем сложность пароля
        if len(password) < 6:
            return False, "Пароль должен содержать минимум 6 символов", None
        
        # Генерируем дискриминатор
        try:
            discriminator = self.user_repo.generate_discriminator(login)
        except ValueError as e:
            return False, str(e), None
        
        # Хэшируем пароль
        password_hash = generate_password_hash(password)
        
        # Создаем пользователя
        try:
            user_id = self.user_repo.create_user(login, password_hash, discriminator)
            
            user = self.user_repo.find_by_id(user_id)
            if user:
                return True, "Пользователь успешно зарегистрирован", user
            else:
                return False, "Ошибка при получении созданного пользователя", None
            
        except Exception as e:
            return False, f"Ошибка при создании пользователя: {e}", None
    
    def authenticate_user(self, login: str, password: str, discriminator: Optional[str] = None) -> Tuple[bool, str, Optional[User]]:
        """Аутентифицирует пользователя.
        
        Args:
            login: Логин пользователя
            password: Пароль пользователя
            discriminator: Дискриминатор (обязателен для всех, кроме admin)
            
        Returns:
            Кортеж (успех, сообщение, пользователь)
        """
        
        if login == 'admin':
            user = self.user_repo.find_admin()
            if not user:
                return False, "Администратор не найден", None
            
            if not check_password_hash(user.password_hash, password):
                return False, "Неверный пароль", None
            
            return True, "Аутентификация успешна", user
        
        if not discriminator:
            return False, "Дискриминатор обязателен", None
        
        user = self.user_repo.find_by_login_and_discriminator(login, discriminator)
        if not user:
            return False, "Неверный логин, дискриминатор или пароль", None
        
        if not check_password_hash(user.password_hash, password):
            return False, "Неверный логин, дискриминатор или пароль", None
        
        return True, "Аутентификация успешна", user
    
    def login_user(self, login: str, password: str, discriminator: Optional[str] = None, remember_me: bool = False) -> Tuple[bool, str, Optional[str]]:
        """Выполняет вход пользователя и возвращает JWT токен.
        
        Args:
            login: Логин пользователя
            password: Пароль пользователя
            discriminator: Дискриминатор (не нужен для admin)
            remember_me: Запомнить пользователя на 30 дней
            
        Returns:
            Кортеж (успех, сообщение, JWT токен)
        """
        
        success, message, user = self.authenticate_user(login, password, discriminator)
        
        if not success or not user:
            return False, message, None
        
        try:
            token = self.jwt_service.generate_token(user.id, remember_me)
            return True, "Вход выполнен успешно", token
        except Exception as e:
            return False, f"Ошибка при генерации токена: {e}", None
    
    def login_user_by_id(self, user_id: int, remember_me: bool = False) -> Tuple[bool, str, Optional[str]]:
        """Выполняет вход пользователя по ID и возвращает JWT токен.
        
        Используется для автоматического входа после регистрации,
        чтобы избежать коллизий при наличии пользователей с одинаковым логином и паролем.
        
        Args:
            user_id: ID пользователя
            remember_me: Запомнить пользователя на 30 дней
            
        Returns:
            Кортеж (успех, сообщение, JWT токен)
        """
        user = self.user_repo.find_by_id(user_id)
        
        if not user:
            return False, "Пользователь не найден", None
        
        try:
            token = self.jwt_service.generate_token(user.id, remember_me)
            return True, "Вход выполнен успешно", token
        except Exception as e:
            return False, f"Ошибка при генерации токена: {e}", None
    
    def get_user_by_token(self, token: str) -> Optional[User]:
        """Получает пользователя по JWT токену.
        
        Args:
            token: JWT токен
            
        Returns:
            Пользователь или None если токен невалиден
        """
        
        try:
            payload = self.jwt_service.verify_token(token)
            if not payload:
                return None
            
            user_id = payload.get('user_id')
            if not user_id:
                return None
            
            user = self.user_repo.find_by_id(user_id)
            return user
        except Exception as e:
            return None
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> Tuple[bool, str]:
        """Изменяет пароль пользователя.
        
        Args:
            user_id: ID пользователя
            old_password: Старый пароль
            new_password: Новый пароль
            
        Returns:
            Кортеж (успех, сообщение)
        """
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return False, "Пользователь не найден"
        
        # Проверяем старый пароль
        if not check_password_hash(user.password_hash, old_password):
            return False, "Неверный старый пароль"
        
        # Проверяем новый пароль
        if len(new_password) < 6:
            return False, "Новый пароль должен содержать минимум 6 символов"
        
        # Обновляем пароль
        password_hash = generate_password_hash(new_password)
        success = self.user_repo.update_password(user_id, password_hash)
        
        if success:
            return True, "Пароль успешно изменен"
        else:
            return False, "Ошибка при изменении пароля"
    
    def get_user_login_options(self, login: str) -> Tuple[bool, list]:
        """Получает варианты входа для логина.
        
        Args:
            login: Логин пользователя
            
        Returns:
            Кортеж (найден ли логин, список дискриминаторов)
        """
        if login == 'admin':
            admin = self.user_repo.find_admin()
            return admin is not None, []
        
        users = self.user_repo.find_by_login(login)
        if not users:
            return False, []
        
        discriminators = [u.discriminator for u in users]
        return True, discriminators