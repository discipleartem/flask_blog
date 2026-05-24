-- Migration: 004_create_posts
-- Description: Создание таблицы постов

-- UP
BEGIN;
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Индексы для производительности
CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_posts_created_at ON posts(created_at);
COMMIT;

-- DOWN
BEGIN;
DROP INDEX idx_posts_created_at;
DROP INDEX idx_posts_user_id;
DROP TABLE posts;
COMMIT;
