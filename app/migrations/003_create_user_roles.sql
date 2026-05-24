-- Migration: 003_create_user_roles
-- Description: Создание таблицы связей пользователей и ролей

-- UP
BEGIN;
CREATE TABLE user_roles (
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);

-- Индексы для производительности
CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_user_roles_role_id ON user_roles(role_id);
COMMIT;

-- DOWN
BEGIN;
DROP INDEX idx_user_roles_role_id;
DROP INDEX idx_user_roles_user_id;
DROP TABLE user_roles;
COMMIT;