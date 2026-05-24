-- Migration: 002_create_roles  
-- Description: Создание таблицы ролей

-- UP
BEGIN;
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,  -- 'admin', 'moderator', 'editor', 'user'
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Базовые роли системы
INSERT INTO roles (name, description) VALUES 
('admin', 'Полный доступ к системе'),
('common', 'Базовый пользователь');

-- Примечание: список ролей определён в app/constants/roles.py
-- При добавлении новых ролей обновляйте BASE_ROLES в модуле констант
COMMIT;

-- DOWN
BEGIN;
DELETE FROM roles;  -- Очищаем базовые роли
DROP TABLE roles;
COMMIT;