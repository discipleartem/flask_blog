"""Сервис для работы с комментариями к постам блога."""

from datetime import datetime
from typing import Optional, List

from app.db.db import get_db
from app.models.comment import Comment


class CommentService:
    """Сервисный слой для работы с комментариями.

    Вся логика работы с базой данных инкапсулирована здесь.
    Модель Comment содержит только данные и базовую бизнес-логику.
    """

    @staticmethod
    def create(author_id: int, post_id: int, content: str) -> Comment:
        """Создаёт новый комментарий.

        Args:
            author_id: ID автора
            post_id: ID поста
            content: Текст комментария

        Returns:
            Comment: созданный комментарий с полной информацией
        """
        db = get_db()
        cursor = db.execute(
            "INSERT INTO comment (author_id, post_id, content) VALUES (?, ?, ?)",
            (author_id, post_id, content),
        )
        db.commit()

        # Получаем созданный комментарий с информацией об авторе
        comment = CommentService.find_by_id(cursor.lastrowid)
        if comment is None:
            raise RuntimeError("Failed to retrieve created comment")
        return comment

    @staticmethod
    def find_by_id(comment_id: int) -> Optional[Comment]:
        """Находит комментарий по ID с информацией об авторе.

        Args:
            comment_id: ID комментария

        Returns:
            Comment или None если не найден
        """
        db = get_db()
        row = db.execute(
            """SELECT c.id, c.author_id, c.post_id, c.content, c.created,
                      u.username as author_username,
                      u.discriminator as author_discriminator
               FROM comment c
               JOIN user u ON c.author_id = u.id
               WHERE c.id = ?""",
            (comment_id,),
        ).fetchone()

        if row is None:
            return None

        return Comment(
            id=row["id"],
            author_id=row["author_id"],
            post_id=row["post_id"],
            content=row["content"],
            created=(
                datetime.fromisoformat(row["created"])
                if isinstance(row["created"], str)
                else row["created"]
            ),
            author_username=row["author_username"],
            author_discriminator=row["author_discriminator"],
        )

    @staticmethod
    def get_by_post_id(post_id: int) -> List[Comment]:
        """Получает все комментарии к посту с информацией об авторах.

        Args:
            post_id: ID поста

        Returns:
            List[Comment]: список комментариев, отсортированных по времени создания
        """
        db = get_db()
        rows = db.execute(
            """SELECT c.id, c.author_id, c.post_id, c.content, c.created,
                      u.username as author_username,
                      u.discriminator as author_discriminator
               FROM comment c
               JOIN user u ON c.author_id = u.id
               WHERE c.post_id = ?
               ORDER BY c.created ASC""",
            (post_id,),
        ).fetchall()

        comments = []
        for row in rows:
            comments.append(
                Comment(
                    id=row["id"],
                    author_id=row["author_id"],
                    post_id=row["post_id"],
                    content=row["content"],
                    created=(
                        datetime.fromisoformat(row["created"])
                        if isinstance(row["created"], str)
                        else row["created"]
                    ),
                    author_username=row["author_username"],
                    author_discriminator=row["author_discriminator"],
                )
            )

        return comments

    @staticmethod
    def delete(comment_id: int, user_id: int) -> bool:
        """Удаляет комментарий (только если пользователь является автором).

        Args:
            comment_id: ID комментария
            user_id: ID пользователя, который пытается удалить

        Returns:
            bool: True если комментарий удалён, False если нет прав или не найден
        """
        db = get_db()

        # Проверяем, что пользователь является автором комментария
        comment = db.execute(
            "SELECT author_id FROM comment WHERE id = ?", (comment_id,)
        ).fetchone()

        if comment is None or comment["author_id"] != user_id:
            return False

        # Удаляем комментарий
        cursor = db.execute("DELETE FROM comment WHERE id = ?", (comment_id,))
        db.commit()

        return cursor.rowcount > 0

    @staticmethod
    def get_count_by_post_id(post_id: int) -> int:
        """Получает количество комментариев к посту.

        Args:
            post_id: ID поста

        Returns:
            int: количество комментариев
        """
        db = get_db()
        row = db.execute(
            "SELECT COUNT(*) as count FROM comment WHERE post_id = ?", (post_id,)
        ).fetchone()

        return row["count"] if row else 0

    @staticmethod
    def update(comment_id: int, user_id: int, content: str) -> bool:
        """Обновляет текст комментария (только если пользователь является автором).

        Args:
            comment_id: ID комментария
            user_id: ID пользователя, который пытается обновить
            content: Новый текст комментария

        Returns:
            bool: True если комментарий обновлён, False если нет прав или не найден
        """
        db = get_db()

        # Проверяем, что пользователь является автором комментария
        comment = db.execute(
            "SELECT author_id FROM comment WHERE id = ?", (comment_id,)
        ).fetchone()

        if comment is None or comment["author_id"] != user_id:
            return False

        # Обновляем комментарий
        cursor = db.execute(
            "UPDATE comment SET content = ? WHERE id = ?", (content, comment_id)
        )
        db.commit()

        return cursor.rowcount > 0
