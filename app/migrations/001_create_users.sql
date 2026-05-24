

-- UP
BEGIN;
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT NOT NULL,
        discriminator TEXT NOT NULL,  -- "0000" для admin, 4 цифры для обычных пользователей
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        -- Композитный уникальный constraint
        CONSTRAINT unique_login_discriminator UNIQUE (login, discriminator)
    );

    -- Индексы
    CREATE INDEX idx_users_login_discriminator ON users(login, discriminator);
    CREATE INDEX idx_users_login ON users(login);  -- Для поиска по логину
COMMIT;


-- DOWN
BEGIN;
    DROP INDEX idx_users_login_discriminator;
    DROP INDEX idx_users_login;
    DROP TABLE users;
COMMIT;
