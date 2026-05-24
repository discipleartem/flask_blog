"""Сервис для работы с постами.

Применяемые паттерны:
- Service Layer — инкапсулирует бизнес-логику работы с постами
- Dependency Injection — внедрение репозиториев
- Validation — валидация данных постов

Применяемые принципы:
- Single Responsibility — только работа с постами
- Explicit is better than implicit — явная валидация
- Fail fast — ранние проверки и ошибки
"""

from typing import List, Optional

from ..models.posts import Post
from ..models.users import User
from ..repositories.post_repo import PostRepository


class PostService:
    """Сервис для работы с постами блога.
    
    Обеспечивает CRUD операции и бизнес-логику для постов.
    """
    
    def __init__(self, post_repo: PostRepository):
        """Инициализирует сервис с зависимостями.
        
        Args:
            post_repo: Репозиторий постов
        """
        self.post_repo = post_repo
    
    def create_post(self, user_id: int, title: str, body: str) -> tuple[bool, str, Optional[Post]]:
        """Создает новый пост.
        
        Args:
            user_id: ID автора
            title: Заголовок поста
            body: Содержание поста
            
        Returns:
            Кортеж (успех, сообщение, пост)
        """
        # Валидация заголовка
        if not title or not title.strip():
            return False, "Заголовок не может быть пустым", None
        
        if len(title.strip()) > 200:
            return False, "Заголовок не может быть длиннее 200 символов", None
        
        # Валидация содержания
        if not body or not body.strip():
            return False, "Содержание поста не может быть пустым", None
        
        if len(body.strip()) > 10000:
            return False, "Содержание поста не может быть длиннее 10000 символов", None
        
        try:
            post_id = self.post_repo.create_post(
                user_id=user_id,
                title=title.strip(),
                body=body.strip()
            )
            
            post = self.post_repo.find_by_id(post_id)
            if post:
                return True, "Пост успешно создан", post
            else:
                return False, "Ошибка при создании поста", None
                
        except Exception as e:
            return False, f"Ошибка при создании поста: {e}", None
    
    def get_post_by_id(self, post_id: int) -> Optional[Post]:
        """Получает пост по ID.
        
        Args:
            post_id: ID поста
            
        Returns:
            Пост или None если не найден
        """
        return self.post_repo.find_by_id(post_id)
    
    def get_all_posts(self, page: int = 1, per_page: int = 10) -> tuple[List[Post], int]:
        """Получает все посты с пагинацией.
        
        Args:
            page: Номер страницы (начиная с 1)
            per_page: Количество постов на странице
            
        Returns:
            Кортеж (список постов, общее количество)
        """
        offset = (page - 1) * per_page
        posts = self.post_repo.find_all(limit=per_page, offset=offset)
        total = self.post_repo.count_posts()
        
        return posts, total
    
    def get_user_posts(self, user_id: int, limit: Optional[int] = None) -> List[Post]:
        """Получает посты указанного пользователя.
        
        Args:
            user_id: ID пользователя
            limit: Максимальное количество постов
            
        Returns:
            Список постов пользователя
        """
        return self.post_repo.find_by_user_id(user_id, limit)
    
    def get_posts_grouped_by_users(self, limit_per_user: int = 3) -> List[Post]:
        """Получает посты сгруппированные по пользователям.
        
        Args:
            limit_per_user: Максимум постов на одного пользователя
            
        Returns:
            Список постов сгруппированных по пользователям
        """
        return self.post_repo.find_grouped_by_users(limit_per_user)
    
    def update_post(self, post_id: int, user_id: int, title: str, body: str, is_admin: bool = False) -> tuple[bool, str, Optional[Post]]:
        """Обновляет пост.
        
        Args:
            post_id: ID поста
            user_id: ID пользователя, пытающегося обновить
            title: Новый заголовок
            body: Новое содержание
            is_admin: Является ли пользователь администратором
            
        Returns:
            Кортеж (успех, сообщение, пост)
        """
        # Получаем пост
        post = self.post_repo.find_by_id(post_id)
        if not post:
            return False, "Пост не найден", None
        
        # Проверяем права на редактирование
        if post.user_id != user_id and not is_admin:
            return False, "У вас нет прав для редактирования этого поста", None
        
        # Валидация заголовка
        if not title or not title.strip():
            return False, "Заголовок не может быть пустым", None
        
        if len(title.strip()) > 200:
            return False, "Заголовок не может быть длиннее 200 символов", None
        
        # Валидация содержания
        if not body or not body.strip():
            return False, "Содержание поста не может быть пустым", None
        
        if len(body.strip()) > 10000:
            return False, "Содержание поста не может быть длиннее 10000 символов", None
        
        try:
            success = self.post_repo.update_post(
                post_id=post_id,
                title=title.strip(),
                body=body.strip()
            )
            
            if success:
                updated_post = self.post_repo.find_by_id(post_id)
                return True, "Пост успешно обновлен", updated_post
            else:
                return False, "Ошибка при обновлении поста", None
                
        except Exception as e:
            return False, f"Ошибка при обновлении поста: {e}", None
    
    def delete_post(self, post_id: int, user_id: int, is_admin: bool = False) -> tuple[bool, str]:
        """Удаляет пост.
        
        Args:
            post_id: ID поста
            user_id: ID пользователя, пытающегося удалить
            is_admin: Является ли пользователь администратором
            
        Returns:
            Кортеж (успех, сообщение)
        """
        # Получаем пост
        post = self.post_repo.find_by_id(post_id)
        if not post:
            return False, "Пост не найден"
        
        # Проверяем права на удаление
        if post.user_id != user_id and not is_admin:
            return False, "У вас нет прав для удаления этого поста"
        
        try:
            success = self.post_repo.delete_post(post_id)
            
            if success:
                return True, "Пост успешно удален"
            else:
                return False, "Ошибка при удалении поста"
                
        except Exception as e:
            return False, f"Ошибка при удалении поста: {e}"
    
    def can_user_edit_post(self, post_id: int, user_id: int, is_admin: bool = False) -> bool:
        """Проверяет, может ли пользователь редактировать пост.
        
        Args:
            post_id: ID поста
            user_id: ID пользователя
            is_admin: Является ли пользователь администратором
            
        Returns:
            True если пользователь может редактировать пост
        """
        post = self.post_repo.find_by_id(post_id)
        if not post:
            return False
        
        return post.user_id == user_id or is_admin
    
    def can_user_delete_post(self, post_id: int, user_id: int, is_admin: bool = False) -> bool:
        """Проверяет, может ли пользователь удалить пост.
        
        Args:
            post_id: ID поста
            user_id: ID пользователя
            is_admin: Является ли пользователь администратором
            
        Returns:
            True если пользователь может удалить пост
        """
        return self.can_user_edit_post(post_id, user_id, is_admin)