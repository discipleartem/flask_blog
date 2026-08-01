-- Flask Blog schema (SQLite)
-- Applied via migrations runner; also kept as the source of truth.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL UNIQUE,
    applied_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL COLLATE NOCASE,
    discriminator TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    is_admin INTEGER NOT NULL DEFAULT 0 CHECK (is_admin IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (name, discriminator)
);

CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    body_source TEXT NOT NULL,
    body_format TEXT NOT NULL DEFAULT 'plaintext',
    author_id INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (author_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    body_source TEXT NOT NULL,
    body_format TEXT NOT NULL DEFAULT 'plaintext',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_posts_author_id ON posts (author_id);
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_comments_post_id ON comments (post_id);
CREATE INDEX IF NOT EXISTS idx_comments_user_id ON comments (user_id);

-- Admin module: PythonAnywhere API monitoring (credentials only via Admin UI).
CREATE TABLE IF NOT EXISTS pa_module_settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    enabled INTEGER NOT NULL DEFAULT 0 CHECK (enabled IN (0, 1)),
    api_token TEXT NOT NULL DEFAULT '',
    username TEXT NOT NULL DEFAULT '',
    api_host TEXT NOT NULL DEFAULT 'www.pythonanywhere.com',
    webapp_domain TEXT NOT NULL DEFAULT '',
    monitor_cpu INTEGER NOT NULL DEFAULT 1 CHECK (monitor_cpu IN (0, 1)),
    monitor_webapps INTEGER NOT NULL DEFAULT 1 CHECK (monitor_webapps IN (0, 1)),
    monitor_schedule INTEGER NOT NULL DEFAULT 0 CHECK (monitor_schedule IN (0, 1)),
    monitor_always_on INTEGER NOT NULL DEFAULT 0 CHECK (monitor_always_on IN (0, 1)),
    monitor_consoles INTEGER NOT NULL DEFAULT 0 CHECK (monitor_consoles IN (0, 1)),
    monitor_disk INTEGER NOT NULL DEFAULT 0 CHECK (monitor_disk IN (0, 1)),
    disk_quota_mib INTEGER NOT NULL DEFAULT 512,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

INSERT OR IGNORE INTO pa_module_settings (id) VALUES (1);
