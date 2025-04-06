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

CREATE TABLE migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Миграция применена: add_updated_at_column_to_articles_table_migration.sql
--==================================================
-- Добавляем колонку updated_at без значения по умолчанию
ALTER TABLE articles  ADD COLUMN updated_at TIMESTAMP;

-- Обновляем существующие записи updated_at текущим временем
UPDATE articles SET updated_at = CURRENT_TIMESTAMP;
--==================================================
 

-- Миграция применена: add_updated_at_column_to_comments_table_migration.sql
--==================================================
-- Добавляем колонку updated_at без значения по умолчанию
ALTER TABLE comments ADD COLUMN updated_at TIMESTAMP;

-- Обновляем существующие записи updated_at текущим временем
UPDATE comments SET updated_at = CURRENT_TIMESTAMP;
--==================================================
 
