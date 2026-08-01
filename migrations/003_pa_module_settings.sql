-- PythonAnywhere admin module: credentials and monitor checkboxes (singleton row id=1).
PRAGMA foreign_keys = ON;

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
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

INSERT OR IGNORE INTO pa_module_settings (id) VALUES (1);
