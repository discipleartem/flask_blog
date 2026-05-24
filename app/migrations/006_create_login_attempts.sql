-- Создание таблицы для отслеживания неудачных попыток входа
CREATE TABLE IF NOT EXISTS login_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT NOT NULL,
    login TEXT NOT NULL,
    attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT 0
);

-- Создание индексов для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_login_attempts_ip ON login_attempts(ip_address);
CREATE INDEX IF NOT EXISTS idx_login_attempts_login ON login_attempts(login);
CREATE INDEX IF NOT EXISTS idx_login_attempts_time ON login_attempts(attempt_time);

-- Создание таблицы для заблокированных аккаунтов
CREATE TABLE IF NOT EXISTS locked_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    locked_until TIMESTAMP NOT NULL,
    lock_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Создание индекса для быстрого поиска заблокированных аккаунтов
CREATE INDEX IF NOT EXISTS idx_locked_accounts_user_id ON locked_accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_locked_accounts_until ON locked_accounts(locked_until);
