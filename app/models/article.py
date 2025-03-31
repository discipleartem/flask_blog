from app.db import get_db
from datetime import datetime

class Article:
    """Model for working with articles in the database"""
    def __init__(self, id, title, content, user_id, created_at, author=None):
        self.id = id
        self.title = title
        self.content = content
        self.user_id = user_id
        self.created_at = created_at
        self.author = author

    @staticmethod
    def get_all():
        """Retrieve all articles"""
        db = get_db()
        articles = db.execute('''
            SELECT a.*, u.username as author 
            FROM articles a 
            JOIN users u ON a.user_id = u.id 
            ORDER BY created_at DESC
        ''').fetchall()
        return [Article(**dict(article)) for article in articles]

    @staticmethod
    def get_by_id(article_id):
        """Retrieve article by ID"""
        db = get_db()
        article = db.execute('''
            SELECT a.*, u.username as author
            FROM articles a
            JOIN users u ON a.user_id = u.id
            WHERE a.id = ?
        ''', (article_id,)).fetchone()

        if article:
            return Article(**dict(article))
        return None

    @staticmethod
    def create(title, content, user_id):
        """Create a new article"""
        db = get_db()
        cursor = db.execute('''
            INSERT INTO articles (title, content, user_id, created_at) 
            VALUES (?, ?, ?, ?)
        ''', (title, content, user_id, datetime.now()))
        db.commit()
        return cursor.lastrowid

    def update(self, title, content):
        """Update article title and content"""
        db = get_db()
        db.execute('''
            UPDATE articles 
            SET title = ?, content = ?, updated_at = ? 
            WHERE id = ?
        ''', (title, content, datetime.now(), self.id))
        db.commit()
        self.title = title
        self.content = content

    def delete(self):
        """Delete article"""
        db = get_db()
        db.execute('DELETE FROM articles WHERE id = ?', (self.id,))
        db.commit()