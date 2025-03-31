-- Схема БД
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    article_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (article_id) REFERENCES articles (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);
-- Applied migration: add_updated_at_coloumn_to_articles_table_migration.sql
ALTER TABLE articles ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;