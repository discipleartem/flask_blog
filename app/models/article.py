from app.db import get_db
from datetime import datetime

class Article:
    """Model for working with articles in the database"""
    def __init__(self, id, title, content, user_id,
                 created_at, updated_at=None, author=None):
        self.id = id
        self.title = title
        self.content = content
        self.user_id = user_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.author = author

    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title[:20]}...', user_id={self.user_id})>"


    @classmethod
    def get_all(cls):
        """Получить все статьи"""
        try:
            db = get_db()

            # Используем LEFT JOIN для получения username, если пользователь не найден - будет NULL
            cursor = db.execute('''
                        SELECT a.id, a.title, a.content, a.created_at, a.updated_at, a.user_id, 
                               COALESCE(u.username, 'unknown') as author
                        FROM articles a 
                        LEFT JOIN users u ON a.user_id = u.id 
                        ORDER BY a.created_at DESC
                    ''')
            rows = cursor.fetchall()

            articles = []
            for row in rows:
                articles.append(cls(
                    id=row['id'],
                    title=row['title'],
                    content=row['content'],
                    user_id=row['user_id'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    author=row['author']
                ))

            return articles
        except Exception as e:
            print(f"DEBUG: Error in get_all(): {e}")
            return []


    @staticmethod
    def get_by_id(article_id):
        """Retrieve article by ID"""
        try:
            db = get_db()
            # Используем LEFT JOIN для получения username, если пользователь не найден - будет NULL
            article_row = db.execute('''
                        SELECT a.id, a.title, a.content, a.created_at, a.updated_at, a.user_id, 
                               COALESCE(u.username, 'unknown') as author
                        FROM articles a 
                        LEFT JOIN users u ON a.user_id = u.id 
                        WHERE a.id = ?
                    ''', (article_id,)).fetchone()

            if article_row:
                return Article(
                    id=article_row['id'],
                    title=article_row['title'],
                    content=article_row['content'],
                    user_id=article_row['user_id'],
                    created_at=article_row['created_at'],
                    updated_at=article_row['updated_at'],
                    author=article_row['author']
                )
            return None
        except Exception as e:
            print(f"DEBUG: Error in get_by_id(): {e}")
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
        self.updated_at = datetime.now()

    def delete(self):
        """Delete article"""
        db = get_db()
        db.execute('DELETE FROM articles WHERE id = ?', (self.id,))
        db.commit()

    @staticmethod
    def search_by_title(search_query):
        """Search articles by title"""
        db = get_db()
        search_pattern = f'%{search_query}%'
        articles = db.execute('''
                    SELECT a.*, COALESCE(u.username, 'unknown') as author 
                    FROM articles a 
                    LEFT JOIN users u ON a.user_id = u.id 
                    WHERE a.title LIKE ?
                    ORDER BY created_at DESC
                ''', (search_pattern,)).fetchall()
        result = [Article(**dict(article)) for article in articles]
        return result

    @staticmethod
    def search_by_content(search_query):
        """Search articles by content"""
        db = get_db()
        search_pattern = f'%{search_query}%'
        articles = db.execute('''
                    SELECT a.*, COALESCE(u.username, 'unknown') as author 
                    FROM articles a 
                    LEFT JOIN users u ON a.user_id = u.id 
                    WHERE a.content LIKE ?
                    ORDER BY created_at DESC
                ''', (search_pattern,)).fetchall()
        result = [Article(**dict(article)) for article in articles]
        return result