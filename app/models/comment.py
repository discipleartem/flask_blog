from datetime import datetime
from app.db import get_db


class Comment:
    """Модель для работы с комментариями в базе данных"""
    def __init__(self, id, content, article_id, user_id, created_at, author=None, updated_at=None):
        self.id = id
        self.content = content
        self.article_id = article_id
        self.user_id = user_id
        self.created_at = created_at
        self.author = author
        self.updated_at = updated_at

    @staticmethod
    def get_by_article_id(article_id):
        """Получение комментариев для статьи"""
        db = get_db()
        comments = db.execute(
            '''SELECT comments.*, users.username as author
               FROM comments 
               JOIN users ON comments.user_id = users.id 
               WHERE article_id = ? 
               ORDER BY created_at DESC''',
            (article_id,)
        ).fetchall()
        return [Comment(**dict(comment)) for comment in comments]

    @staticmethod
    def get_by_id(article_id, comment_id):
        """Получение комментария по ID"""
        db = get_db()
        comment = db.execute('SELECT * FROM comments WHERE id = ? AND article_id = ?', (comment_id, article_id)).fetchone()
        return Comment(**dict(comment)) if comment else None

    @staticmethod
    def create(content, article_id, user_id):
        """Создание нового комментария"""
        db = get_db()
        cursor = db.execute(
            'INSERT INTO comments (content, article_id, user_id) VALUES (?, ?, ?)',
            (content, article_id, user_id)
        )
        db.commit()
        return cursor.lastrowid

    def update(self, content):
        """Обновление комментария"""
        db = get_db()
        db.execute("""
            UPDATE comments 
            SET content = ?, updated_at = ?
            WHERE id = ? AND article_id = ?""",
            (content, datetime.now(), self.id, self.article_id)
        )
        db.commit()
        self.content = content
        self.updated_at = datetime.now()

    def delete(self):
        """Удаление комментария"""
        db = get_db()
        db.execute('DELETE FROM comments WHERE id = ?', (self.id,))
        db.commit()