from app.db import get_db


class Comment:
    """Модель для работы с комментариями в базе данных"""
    def __init__(self, id, content, article_id, user_id, created_at, author=None):
        self.id = id
        self.content = content
        self.article_id = article_id
        self.user_id = user_id
        self.created_at = created_at
        self.author = author

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
    def create(content, article_id, user_id):
        """Создание нового комментария"""
        db = get_db()
        cursor = db.execute(
            'INSERT INTO comments (content, article_id, user_id) VALUES (?, ?, ?)',
            (content, article_id, user_id)
        )
        db.commit()
        return cursor.lastrowid

    def delete(self):
        """Удаление комментария"""
        db = get_db()
        db.execute('DELETE FROM comments WHERE id = ?', (self.id,))
        db.commit()