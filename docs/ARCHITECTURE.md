# 🏗️ Архитектура проекта Flask Blog

**Версия:** 0.1.0 | **Дата:** Май 2026

---

## Оглавление

1. [Обзор проекта](#1-обзор-проекта)
2. [Архитектура](#2-архитектура)
3. [Структура проекта](#3-структура-проекта)
4. [Применяемые паттерны проектирования](#4-применяемые-паттерны-проектирования)
5. [Применяемые принципы программирования](#5-применяемые-принципы-программирования)

---

## 1. Обзор проекта

**Flask Blog** — это простой, но функционально полный блог на Flask 3+ с самописной системой авторизации, системой ролей, дискриминаторами пользователей, брутфорс-защитой и чистой архитектурой.

### Ключевые возможности

| Возможность | Описание |
|---|---|
| 🔐 Аутентификация | Самописная JWT-авторизация (HS256) через cookies |
| 👤 Дискриминаторы | Несколько аккаунтов с одинаковым логином (login#1234) |
| 🛡️ Роли | Admin, Moderator, User — распределённая система прав |
| 🚫 Брутфорс-защита | Flask-Limiter + LoginAttemptService |
| 🌓 Темизация | Тёмная/светлая тема с сохранением в localStorage + cookie |
| 📝 CRUD блога | Создание, чтение, обновление, удаление постов и комментариев |
| 🗄️ Чистый SQL | Никакого ORM — ручные SQL-запросы через собственный слой db.py |
| 📦 Миграции | Ручные SQL-миграции с системой версионирования |
| 🧪 Тестирование | pytest с поддержкой покрытия |

---

## 2. Архитектура

Проект следует принципам **Чистой Архитектуры** (Clean Architecture) Роберта Мартина, адаптированной под Flask:

```
┌────────────────────────────────────────────────────────────┐
│                    Frameworks & Drivers                     │
│  (Flask, Flask-Limiter, Jinja2, SQLite, python-dotenv)     │
├────────────────────────────────────────────────────────────┤
│                  Interface Adapters                         │
│  app/views/  (Blueprints — контроллеры)                    │
│  app/auth.py (JWT middleware)                              │
│  app/cli.py  (CLI команды)                                 │
│  app/templates/ (Jinja2 шаблоны)                           │
├────────────────────────────────────────────────────────────┤
│                      Use Cases                              │
│  app/services/  (бизнес-логика)                            │
│  app/repositories/ (абстракция доступа к данным)           │
├────────────────────────────────────────────────────────────┤
│                       Entities                              │
│  app/models/  (бизнес-сущности)                            │
│  app/constants/ (константы)                                │
└────────────────────────────────────────────────────────────┘
```

### Направление зависимостей

```
Внешние слои ──► Внутренние слои
Views ──► Services ──► Repositories ──► Models
  │            │             │
  └────────────┴─────────────┴────► db.py (доступ к SQLite)
```

- **Models** не зависят ни от чего, кроме констант
- **Repositories** зависят от Models и db.py
- **Services** зависят от Repositories
- **Views** зависят от Services

---

## 3. Структура проекта

```
flask_blog/
├── run.py                         # Точка входа
├── pyproject.toml                  # Зависимости и конфигурация инструментов
├── Makefile                        # Команды для разработки
├── .env                            # Переменные окружения
├── .flaskenv                       # Flask переменные окружения
├── .gitignore
├── LICENSE
├── README.md
│
├── app/                            # Основной пакет приложения
│   ├── __init__.py                 # Фабрика приложения (create_app)
│   ├── config.py                   # Конфигурационные классы
│   ├── db.py                       # Слой доступа к данным (SQLite)
│   ├── auth.py                     # JWT middleware и хелперы
│   ├── cli.py                      # CLI команды (flask migrate, seed, etc.)
│   │
│   ├── constants/                  # Константы
│   │   └── roles.py                # Системные роли (Admin, Moderator, User)
│   │
│   ├── models/                     # Бизнес-сущности (DTO)
│   │   ├── __init__.py
│   │   ├── users.py                # User
│   │   ├── posts.py                # Post
│   │   └── comments.py             # Comment
│   │
│   ├── repositories/               # Репозитории (доступ к данным)
│   │   ├── __init__.py
│   │   ├── user_repo.py            # UserRepository
│   │   ├── post_repo.py            # PostRepository
│   │   └── comment_repo.py         # CommentRepository
│   │
│   ├── services/                   # Бизнес-логика
│   │   ├── __init__.py
│   │   ├── jwt_service.py          # JWT-сервис (самописный HS256)
│   │   ├── user_auth_service.py    # Аутентификация и регистрация
│   │   ├── post_service.py         # Логика постов
│   │   ├── comment_service.py      # Логика комментариев
│   │   ├── csrf_service.py         # CSRF-защита
│   │   ├── login_attempt_service.py # Защита от брутфорса
│   │   └── role_service.py         # Управление ролями
│   │
│   ├── views/                      # Blueprints (контроллеры)
│   │   ├── __init__.py
│   │   ├── auth.py                 # auth_bp (/auth/*)
│   │   └── blog.py                 # blog_bp (/ — блог)
│   │
│   ├── templates/                  # Jinja2 шаблоны
│   │   ├── base.html               # Базовый каркас
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   ├── register.html
│   │   │   └── select_account.html
│   │   ├── blog/
│   │   │   ├── index.html
│   │   │   ├── create_post.html
│   │   │   └── post_detail.html
│   │   └── errors/
│   │       ├── 404.html
│   │       └── 500.html
│   │
│   ├── static/                     # Статические файлы
│   │   ├── css/
│   │   │   ├── style.css
│   │   │   └── blog-layout.css
│   │   └── js/
│   │       ├── navbar.js
│   │       ├── theme-toggle.js
│   │       ├── auth-cookies.js
│   │       └── login-discriminator-update.js
│   │
│   └── migrations/                 # SQL миграции
│       ├── migration_runner.py
│       ├── schema.sql
│       └── *.sql (000-006)
│
├── src/                            # Заготовка под чистую архитектуру
│   ├── entities/
│   ├── interfaces/
│   ├── use_cases/
│   ├── frameworks/
│   └── web/
│
├── tests/                          # Тесты
│   ├── __init__.py
│   └── test_basic.py
│
└── docs/                           # Документация
    ├── INDEX.md
    ├── ARCHITECTURE.md
    ├── LAYERS.md
    ├── DATABASE.md
    ├── SECURITY.md
    ├── FRONTEND.md
    ├── DEVELOPMENT.md
    └── ...
```

---

## 4. Применяемые паттерны проектирования

### Порождающие (Creational)

| Паттерн | Где применяется |
|---|---|
| **Factory Method** | `create_app()` — фабрика Flask-приложений; `User.create_new()` |
| **Singleton** | `Config` (через модуль) |
| **Builder** | Сборка приложения в `create_app()` |

### Структурные (Structural)

| Паттерн | Где применяется |
|---|---|
| **Facade** | `__init__.py` файлы в models, repositories, services — единые точки входа |
| **Adapter** | `db.py` — адаптер над SQLite; `repositories/` — адаптер между моделями и SQL |
| **Proxy** | `LoginAttemptService` — прокси перед проверкой пароля |
| **Composite** | Blueprints — композиция маршрутов |

### Поведенческие (Behavioral)

| Паттерн | Где применяется |
|---|---|
| **Strategy** | Классы конфигурации (`DevelopmentConfig`, `ProductionConfig`, `TestingConfig`) |
| **Observer** | Flask сигналы, `before_request` хуки |
| **Command** | CLI команды (`flask migrate`, `flask seed`, etc.) |
| **Template Method** | `base.html` — базовый шаблон с блоками |
| **Chain of Responsibility** | `before_request` middleware chain |
| **Repository** | Репозитории — абстракция над хранилищем |

### Архитектурные

| Паттерн | Где применяется |
|---|---|
| **Clean Architecture** | Разделение на слои (Models → Repositories → Services → Views) |
| **Dependency Injection** | Внедрение репозиториев и сервисов в `create_app()` |
| **Application Factory** | `create_app(config_class)` |
| **MVC** | Models (модели) / Views (шаблоны) / Controllers (blueprints) |
| **Service Layer** | `app/services/` — бизнес-логика |
| **DTO** | Dataclass модели (`User`, `Post`, `Comment`) |
| **Middleware** | JWT-авторизация через `before_request` |

---

## 5. Применяемые принципы программирования

| Принцип | Применение |
|---|---|
| **DRY** | Общая логика БД в `db.py`, общий `base.html` |
| **KISS** | Чистый SQL вместо ORM, простые dataclass-модели |
| **YAGNI** | Нет преждевременных абстракций, CSRF в разработке |
| **SRP** | Каждый класс/модуль имеет одну ответственность |
| **OCP** | Конфигурации расширяются через наследование `Config` |
| **DIP** | Сервисы зависят от абстракций репозиториев |
| **ISP** | Раздельные репозитории (`UserRepository`, `PostRepository`, `CommentRepository`) |
| **Explicit > Implicit** | Явные типы, явные параметры функций |
| **Readability counts** | Понятные имена, docstrings на русском, типизация |

---

*Документация создана на основе анализа исходного кода, май 2026.*