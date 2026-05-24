# 🗄️ База данных Flask Blog

**Версия:** 0.1.0 | **Дата:** Май 2026

---

## Оглавление

1. [Схема БД](#1-схема-бд)
2. [Системные роли](#2-системные-роли)
3. [Система миграций](#3-система-миграций)
4. [Слой доступа к данным](#4-слой-доступа-к-данным)

---

## 1. Схема БД

Проект использует **SQLite** с чистым SQL (без ORM). Все таблицы используют `INTEGER PRIMARY KEY AUTOINCREMENT` для идентификаторов и `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` для временных меток.

### Полная схема

```sql
-- Пользователи
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT NOT NULL,
    discriminator TEXT,              -- NULL для первого (основного) аккаунта
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(login, discriminator)
);

-- Роли
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,       -- admin, moderator, user
    description TEXT
);

-- Связь пользователь-роль (Many-to-Many)
CREATE TABLE user_roles (
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);

-- Посты
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Комментарии
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    body TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Попытки входа (брутфорс-защита)
CREATE TABLE login_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    identifier TEXT NOT NULL,         -- IP-адрес или логин
    attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN NOT NULL DEFAULT 0
);

-- Служебная таблица миграций
CREATE TABLE migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL UNIQUE,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### ER-диаграмма (логическая)

```
users 1───* posts          (user_id → users.id, CASCADE)
users 1───* comments       (user_id → users.id, CASCADE)
posts 1───* comments       (post_id → posts.id, CASCADE)
users *───* roles          (через user_roles, CASCADE)
users 1───* login_attempts (identifier — логин или IP)
```

### Особенности схемы

| Таблица | Ключевая особенность |
|---|---|
| `users` | `UNIQUE(login, discriminator)` — позволяет несколько аккаунтов с одинаковым логином |
| `users.discriminator` | `NULL` для первого (основного) аккаунта, 4-значный код для последующих |
| `user_roles` | Составной первичный ключ `(user_id, role_id)`, каскадное удаление |
| `posts` / `comments` | Каскадное удаление при удалении пользователя |
| `login_attempts` | Используется `LoginAttemptService` для блокировки после 5 неудачных попыток |
| `migrations` | Служебная таблица версионирования для `MigrationRunner` |

---

## 2. Системные роли

Роли определены в `app/constants/roles.py` и загружаются в БД при миграции `002_create_roles.sql`.

| Роль | Константа | Описание |
|---|---|---|
| `admin` | `SystemRole.ADMIN` | Полный доступ: управление пользователями, удаление любого контента, назначение ролей |
| `moderator` | `SystemRole.MODERATOR` | Может удалять чужие комментарии |
| `user` | `SystemRole.USER` | Базовая роль: создание/редактирование своих постов и комментариев |

### Назначение ролей

Роли назначаются через `UserRepository.add_role()` и `RoleService.assign_role()`. При регистрации пользователь автоматически получает роль `user` (через `User.create_new()`).

### Проверка прав

- `User.is_admin` — проверка `admin`
- `User.has_role(role_name)` — проверка любой роли
- `RoleService.is_admin(user_id)` / `RoleService.is_moderator(user_id)` — сервисные методы
- В views: проверка `current_user.is_admin` для доступа к админ-функциям

### Резервирование логинов

Следующие логины зарезервированы и не могут быть использованы при регистрации (проверка в `UserRepository`):
`admin`, `moderator`, `system`, `root`, `owner`

---

## 3. Система миграций

Миграции — ручные SQL-файлы с префиксом-номером, применяемые последовательно через `MigrationRunner`.

### Файлы миграций

| Файл | Создаваемая таблица | Содержание |
|---|---|---|
| `000_create_migrations.sql` | `migrations` | Служебная таблица для отслеживания применённых миграций |
| `001_create_users.sql` | `users` | id, login, discriminator, password_hash, created_at, updated_at |
| `002_create_roles.sql` | `roles` | id, name, description; начальные значения: admin, moderator, user |
| `003_create_user_roles.sql` | `user_roles` | Связь Many-to-Many: user_id + role_id |
| `004_create_posts.sql` | `posts` | id, user_id, title, body, created_at, updated_at |
| `005_create_comments.sql` | `comments` | id, post_id, user_id, body, created_at |
| `006_create_login_attempts.sql` | `login_attempts` | id, identifier, attempt_time, success |

### MigrationRunner (`app/migrations/migration_runner.py`)

**Принцип работы:**
1. Сканирует директорию `app/migrations/` на наличие `.sql` файлов
2. Сравнивает с записями в таблице `migrations`
3. Применяет только новые миграции в порядке возрастания номеров
4. Поддерживает откат (rollback) при ошибке

**CLI команды:**

| Команда | Назначение |
|---|---|
| `flask migrate` | Применить все неприменённые миграции |
| `flask migrate-upgrade` | Обновить схему БД (алиас) |
| `flask db-reset` | Полный сброс и пересоздание БД (удаление + пересоздание + миграции + seed) |
| `flask seed` | Наполнить БД тестовыми данными (пользователи, посты, комментарии) |

### Полная схема (`app/migrations/schema.sql`)

Содержит полный DDL для создания всех таблиц. Используется при инициализации БД (`db.init_db()`) и сбросе (`flask db-reset`).

---

## 4. Слой доступа к данным

Модуль `app/db.py` предоставляет абстракцию над SQLite. Все запросы параметризованные (защита от SQL-инъекций).

### Ключевые функции

| Функция | Назначение | Возвращает |
|---|---|---|
| `get_db_path()` | Извлекает путь к файлу БД из `DATABASE_URL` | `str` |
| `get_db()` | Контекстный менеджер соединения | `sqlite3.Connection` |
| `execute_query()` | Универсальный SELECT (fetch_one / fetch_all) | `dict` / `list[dict]` / `None` |
| `execute_insert()` | INSERT с возвратом `lastrowid` | `int` |
| `execute_update()` | UPDATE/DELETE с возвратом `rowcount` | `int` |
| `execute_batch()` | Пакетное выполнение (`executemany`) | `int` |
| `init_db()` | Инициализация БД из `schema.sql` | `None` |

### Конфигурация подключения

```python
# config.py
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///blog.db')

# Поддерживаемые форматы:
# sqlite:///blog.db       → файл blog.db в корне проекта
# sqlite:///:memory:      → в памяти (для тестов)
# sqlite:///path/to/db    → абсолютный путь

# Реализация в db.py:
# get_db_path() парсит DATABASE_URL и извлекает путь
```

### Особенности

- **`sqlite3.Row`** как `row_factory` — доступ к полям по имени (как словарь) и по индексу
- **Автоматический rollback** при исключениях внутри `get_db()` контекстного менеджера
- **WAL-режим** не используется (стандартный режим SQLite)
- **Без пула соединений** — каждое обращение открывает новое соединение (приемлемо для SQLite)

---

*Документация создана на основе анализа исходного кода, май 2026.*