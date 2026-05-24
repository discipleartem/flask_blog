"""Сервис для работы с комментариями.

Применяемые паттерны:
- Service Layer — инкапсулирует бизнес-логику работы с комментариями
- Dependency Injection — внедрение репозиториев
- Validation — валидация данных комментариев

Применяемые принципы:
- Single Responsibility — только работа с комментариями
- Explicit is better than implicit — явная валидация
- Fail fast — ранние проверки и ошибки
"""

from typing import List, Optional

from ..models.comments import Comment
from ..models.posts import Post
from ..repositories.comment_repo import CommentRepository
from ..repositories.post_repo import PostRepository


class CommentService:
    """Сервис для работы с комментариями к постам.
    
    Обеспечивает CRUD операции и бизнес-логику для комментариев.
    """
    
    def __init__(self, comment_repo: CommentRepository, post_repo: PostRepository):
        """Инициализирует сервис с зависимостями.
        
        Args:
            comment_repo: Репозиторий комментариев
            post_repo: Репозиторий постов
        """
        self.comment_repo = comment_repo
        self.post_repo = post_repo
    
    def create_comment(self, post_id: int, user_id: int, body: str) -> tuple[bool, str, Optional[Comment]]:
        """Создает новый комментарий.
        
        Args:
            post_id: ID поста
            user_id: ID автора комментария
            body: Содержание комментария
            
        Returns:
            Кортеж (успех, сообщение, комментарий)
        """
        # Проверяем существование поста
        post = self.post_repo.find_by_id(post_id)
        if not post:
            return False, "Пост не найден", None
        
        # Валидация содержания
        if not body or not body.strip():
            return False, "Содержание комментария не может быть пустым", None
        
        if len(body.strip()) > 2000:
            return False, "Комментарий не может быть длиннее 2000 символов", None
        
        try:
            comment_id = self.comment_repo.create_comment(
                post_id=post_id,
                user_id=user_id,
                body=body.strip()
            )
            
            comment = self.comment_repo.find_by_id(comment_id)
            if comment:
                return True, "Комментарий успешно добавлен", comment
            else:
                return False, "Ошибка при добавлении комментария", None
                
        except Exception as e:
            return False, f"Ошибка при добавлении комментария: {e}", None
    
    def get_comment_by_id(self, comment_id: int) -> Optional[Comment]:
        """Получает комментарий по ID.
        
        Args:
            comment_id: ID комментария
            
        Returns:
            Комментарий или None если не найден
        """
        return self.comment_repo.find_by_id(comment_id)
    
    def get_post_comments(self, post_id: int, limit: Optional[int] = None) -> List[Comment]:
        """Получает комментарии к посту.
        
        Args:
            post_id: ID поста
            limit: Максимальное количество комментариев
            
        Returns:
            Список комментариев к посту
        """
        # Проверяем существование поста
        post = self.post_repo.find_by_id(post_id)
        if not post:
            return []
        
        return self.comment_repo.find_by_post_id(post_id, limit)
    
    def get_user_comments(self, user_id: int, limit: Optional[int] = None) -> List[Comment]:
        """Получает комментарии пользователя.
        
        Args:
            user_id: ID пользователя
            limit: Максимальное количество комментариев
            
        Returns:
            Список комментариев пользователя
        """
        return self.comment_repo.find_by_user_id(user_id, limit)
    
    def update_comment(self, comment_id: int, user_id: int, body: str, is_admin: bool = False) -> tuple[bool, str, Optional[Comment]]:
        """Обновляет комментарий.
        
        Args:
            comment_id: ID комментария
            user_id: ID пользователя, пытающегося обновить
            body: Новое содержание
            is_admin: Является ли пользователь администратором
            
        Returns:
            Кортеж (успех, сообщение, комментарий)
        """
        # Получаем комментарий
        comment = self.comment_repo.find_by_id(comment_id)
        if not comment:
            return False, "Комментарий не найден", None
        
        # Проверяем права на редактирование
        if comment.user_id != user_id and not is_admin:
            return False, "У вас нет прав для редактирования этого комментария", None
        
        # Валидация содержания
        if not body or not body.strip():
            return False, "Содержание комментария не может быть пустым", None
        
        if len(body.strip()) > 2000:
            return False, "Комментарий не может быть длиннее 2000 символов", None
        
        try:
            success = self.comment_repo.update_comment(
                comment_id=comment_id,
                body=body.strip()
            )
            
            if success:
                updated_comment = self.comment_repo.find_by_id(comment_id)
                return True, "Комментарий успешно обновлен", updated_comment
            else:
                return False, "Ошибка при обновлении комментария", None
                
        except Exception as e:
            return False, f"Ошибка при обновлении комментария: {e}", None
    
    def delete_comment(self, comment_id: int, user_id: int, is_admin: bool = False) -> tuple[bool, str]:
        """Удаляет комментарий.
        
        Args:
            comment_id: ID комментария
            user_id: ID пользователя, пытающегося удалить
            is_admin: Является ли пользователь администратором
            
        Returns:
            Кортеж (успех, сообщение)
        """
        # Получаем комментарий
        comment = self.comment_repo.find_by_id(comment_id)
        if not comment:
            return False, "Комментарий не найден"
        
        # Проверяем права на удаление
        if comment.user_id != user_id and not is_admin:
            return False, "У вас нет прав для удаления этого комментария"
        
        try:
            success = self.comment_repo.delete_comment(comment_id)
            
            if success:
                return True, "Комментарий успешно удален"
            else:
                return False, "Ошибка при удалении комментария"
                
        except Exception as e:
            return False, f"Ошибка при удалении комментария: {e}"
    
    def get_post_comments_count(self, post_id: int) -> int:
        """Получает количество комментариев к посту.
        
        Args:
            post_id: ID поста
            
        Returns:
            Количество комментариев
        """
        return self.comment_repo.count_comments(post_id=post_id)
    
    def get_user_comments_count(self, user_id: int) -> int:
        """Получает количество комментариев пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Количество комментариев
        """
        return self.comment_repo.count_comments(user_id=user_id)
    
    def can_user_edit_comment(self, comment_id: int, user_id: int, is_admin: bool = False) -> bool:
        """Проверяет, может ли пользователь редактировать комментарий.
        
        Args:
            comment_id: ID комментария
            user_id: ID пользователя
            is_admin: Является ли пользователь администратором
            
        Returns:
            True если пользователь может редактировать комментарий
        """
        comment = self.comment_repo.find_by_id(comment_id)
        if not comment:
            return False
        
        return comment.user_id == user_id or is_admin
    
    def can_user_delete_comment(self, comment_id: int, user_id: int, is_admin: bool = False) -> bool:
        """Проверяет, может ли пользователь удалить комментарий.
        
        Args:
            comment_id: ID комментария
            user_id: ID пользователя
            is_admin: Является ли пользователь администратором
            
        Returns:
            True если пользователь может удалить комментарий
        """
        return self.can_user_edit_comment(comment_id, user_id, is_admin)