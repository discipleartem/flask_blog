# 🧱 Слои приложения Flask Blog

**Версия:** 0.1.0 | **Дата:** Май 2026

---

## Оглавление

1. [Точка входа (run.py)](#1-точка-входа-runpy)
2. [Фабрика приложения (app/__init__.py)](#2-фабрика-приложения-app__init__py)
3. [Конфигурация (app/config.py)](#3-конфигурация-appconfigpy)
4. [Слой доступа к данным (app/db.py)](#4-слой-доступа-к-данным-appdbpy)
5. [Модели (app/models/)](#5-модели-appmodels)
6. [Репозитории (app/repositories/)](#6-репозитории-apprepositories)
7. [Сервисы (app/services/)](#7-сервисы-appservices)
8. [Представления (app/views/)](#8-представления-appviews)
9. [Аутентификация (app/auth.py)](#9-аутентификация-appauthpy)
10. [CLI (app/cli.py)](#10-cli-appclipy)

---

## 1. Точка входа (`run.py`)

Модуль запуска приложения. Импортирует фабрику `create_app` и запускает Flask development server.

```python
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=app.config.get('PORT', 5000))
```

**Паттерн:** Entry Point, делегирование создания приложения фабрике.

---

## 2. Фабрика приложения (`app/__init__.py`)

**Функция `create_app(config_class)`** — центральная точка сборки приложения:

1. Загружает переменные окружения из `.env` через `dotenv.load_dotenv()`
2. Создаёт экземпляр Flask с явными параметрами (`static_folder`, `template_folder`)
3. Применяет конфигурацию: `config_class.init_app(app)` + `app.config.from_object(config_class)`
4. Инициализирует `Flask-Limiter` (защита от брутфорса, `memory://` хранилище)
5. Настраивает логирование (только ошибки в production)
6. Инициализирует БД: `db.init_db()`
7. Регистрирует CLI команды: `cli.register_cli_commands(app)`
8. Создаёт репозитории и сервисы (Dependency Injection в `app`):
   - `UserRepository`, `PostRepository`, `CommentRepository`
   - `JWTService`, `UserAuthService`, `PostService`, `CommentService`
9. Регистрирует обработчики ошибок (404, 500, Exception)
10. Подключает JWT middleware: `app.before_request(auth.load_user_from_token)`
11. Регистрирует Blueprints: `auth_bp` и `blog_bp`
12. Настраивает context processors: `csrf_token` (заглушка), `current_user`
13. Добавляет фильтр шаблонов: `nl2br` (переносы строк → `<br>`)

**Паттерны:**
- **Factory Method** — создание разных конфигураций приложения
- **Dependency Injection** — внедрение репозиториев и сервисов в приложение
- **Middleware** — JWT-авторизация через `before_request`

---

## 3. Конфигурация (`app/config.py`)

Иерархия классов конфигурации:

| Класс | Назначение | Особенности |
|---|---|---|
| `Config` | Базовая конфигурация | Загружает из `os.getenv()`, значения по умолчанию |
| `DevelopmentConfig` | Разработка | `DEBUG=True` |
| `ProductionConfig` | Продакшн | `DEBUG=False`, `SESSION_COOKIE_SECURE=True`, логи в файл `logs/blog.log` |
| `TestingConfig` | Тестирование | `TESTING=True`, SQLite в памяти, CSRF отключён |

**Ключевые параметры:**
- `SECRET_KEY` — из `os.getenv` (по умолчанию `'dev-secret-key-change-in-production'`)
- `DATABASE_URL` — `sqlite:///blog.db`
- `SESSION_COOKIE_DURATION` — 7 дней
- `SESSION_COOKIE_SECURE` — только HTTPS в production
- `SESSION_COOKIE_HTTPONLY` — `True`
- `SESSION_COOKIE_SAMESITE` — `'lax'`

**Доступные конфиги:** `config['development']`, `config['production']`, `config['testing']`, `config['default']`

**Паттерны:**
- **Configuration Object** — инкапсуляция настроек в классы
- **Environment Variable** — загрузка из окружения
- **Strategy** — разные стратегии конфигурации для разных сред

---

## 4. Слой доступа к данным (`app/db.py`)

Модуль предоставляет абстракцию над SQLite без использования ORM.

**Ключевые функции:**

| Функция | Назначение | Возвращает |
|---|---|---|
| `get_db_path()` | Извлекает путь к файлу БД из `DATABASE_URL` | `str` |
| `get_db()` | Контекстный менеджер соединения с SQLite | `sqlite3.Connection` |
| `execute_query()` | Универсальное выполнение SQL | `dict` или `list[dict]` или `None` |
| `execute_insert()` | INSERT с возвратом `lastrowid` | `int` |
| `execute_update()` | UPDATE/DELETE с возвратом `rowcount` | `int` |
| `execute_batch()` | Пакетное выполнение (`executemany`) | `int` (общее количество строк) |
| `init_db()` | Инициализация БД (создание таблиц из `schema.sql`) | `None` |

**Особенности:**
- Использует `sqlite3.Row` в качестве `row_factory` (доступ к полям как к словарю)
- Автоматический `rollback` при исключениях
- Параметризованные запросы (защита от SQL-инъекций)
- Все функции работают через `g` (Flask application context)

**Паттерны:**
- **Database Access Layer** — изоляция SQL-логики
- **Context Manager** — безопасное управление соединениями

---

## 5. Модели (`app/models/`)

Бизнес-сущности, реализованные как **dataclasses** (DTO — Data Transfer Objects). Не содержат ORM-логики.

### User (`app/models/users.py`)

```python
@dataclass
class User:
    id: int
    login: str
    discriminator: Optional[str]
    password_hash: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    _roles: List[str] = field(default_factory=list)
```

| Свойство | Описание |
|---|---|
| `login_full` | `login#discriminator` (например, `john#1234`) |
| `is_common` | `True`, если нет дискриминатора |
| `roles` | Список ролей пользователя |
| `is_admin` | Проверка роли `admin` |
| `has_role(role)` | Проверка конкретной роли |
| `created_date_formatted` | Отформатированная дата создания |

**Фабричный метод:** `User.create_new(login, password_hash, discriminator=None)` — создаёт пользователя с ролью `user` по умолчанию.

### Post (`app/models/posts.py`)

```python
@dataclass
class Post:
    id: Optional[int]
    user_id: int
    title: str
    body: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    author_login: Optional[str] = None
```

| Свойство | Описание |
|---|---|
| `created_date_formatted` | Отформатированная дата создания |
| `body_preview(max_length=200)` | Превью текста поста |
| `is_author(user_id)` | Проверка авторства |

### Comment (`app/models/comments.py`)

```python
@dataclass
class Comment:
    id: Optional[int]
    post_id: int
    user_id: int
    body: str
    created_at: Optional[datetime] = None
    author_login: Optional[str] = None
```

| Свойство | Описание |
|---|---|
| `created_date_formatted` | Отформатированная дата создания |
| `is_author(user_id)` | Проверка авторства |

**Паттерны:**
- **DTO (Data Transfer Object)** — чистые структуры данных
- **Immutable Object** — через `@dataclass` с явными полями
- **Factory Method** — `User.create_new()`

---

## 6. Репозитории (`app/repositories/`)

Абстракция доступа к данным. Каждый репозиторий содержит SQL-запросы и преобразует строки БД в модели.

### UserRepository (`app/repositories/user_repo.py`)

| Метод | SQL | Возвращает |
|---|---|---|
| `find_by_id(user_id)` | `SELECT * FROM users WHERE id = ?` | `User` или `None` |
| `find_by_login(login)` | `SELECT * FROM users WHERE login = ?` | `list[User]` |
| `find_by_login_discriminator(login, discriminator)` | `SELECT ... WHERE login = ? AND discriminator = ?` | `User` или `None` |
| `create(user)` | `INSERT INTO users ...` | `User` (с присвоенным id) |
| `update(user)` | `UPDATE users SET ... WHERE id = ?` | `User` |
| `delete(user_id)` | `DELETE FROM users WHERE id = ?` | `bool` |
| `get_all()` | `SELECT ... FROM users` | `list[User]` |
| `exists_by_login(login)` | `SELECT COUNT(*) FROM users WHERE login = ?` | `bool` |
| **Работа с ролями:** | | |
| `get_roles(user_id)` | `SELECT r.name FROM roles r JOIN user_roles ur ...` | `list[str]` |
| `add_role(user_id, role_name)` | `INSERT INTO user_roles ...` + поиск role.id | `bool` |
| `remove_role(user_id, role_name)` | `DELETE FROM user_roles ...` | `bool` |
| `generate_discriminator(login)` | Поиск максимального дискриминатора для логина | `str` (4 цифры) |

**Особенности:**
- Резервирование логинов: `admin`, `moderator`, `system`, `root`, `owner`
- Дискриминаторы — 4-значный код (0001-9999), уникальный в рамках одного логина
- Автоматическая загрузка ролей при создании User из строки БД

### PostRepository (`app/repositories/post_repo.py`)

| Метод | Возвращает |
|---|---|
| `find_by_id(post_id)` | `Post` или `None` |
| `find_all()` | `list[Post]` (с `author_login` через JOIN) |
| `find_by_user_id(user_id)` | `list[Post]` |
| `create(post)` | `Post` с id |
| `update(post)` | `Post` |
| `delete(post_id)` | `bool` |

### CommentRepository (`app/repositories/comment_repo.py`)

| Метод | Возвращает |
|---|---|
| `find_by_id(comment_id)` | `Comment` или `None` |
| `find_by_post_id(post_id)` | `list[Comment]` (с `author_login`) |
| `create(comment)` | `Comment` с id |
| `update(comment)` | `Comment` |
| `delete(comment_id)` | `bool` |
| `count_by_post_id(post_id)` | `int` |

**Паттерны:**
- **Repository Pattern** — абстракция над хранилищем данных
- **Data Mapper** — преобразование строк БД в объекты моделей

---

## 7. Сервисы (`app/services/`)

Слой бизнес-логики. Координирует работу репозиториев и внешних сервисов.

### JWTService (`app/services/jwt_service.py`)

**Самописная реализация JWT без внешних библиотек.**

Алгоритм: **HS256** (жёстко закодирован, не хранится в токене)

**Методы:**

| Метод | Назначение |
|---|---|
| `generate_token(user_id, duration=None)` | Создаёт JWT: `base64(header).base64(payload).signature` |
| `verify_token(token)` | Проверяет подпись и срок действия |
| `decode_token(token)` | Извлекает payload без проверки |
| `get_token_from_request()` | Извлекает токен из cookies приоритетно из `jwt_token`, затем `remember_token` |
| `set_token_cookie(response, token, duration)` | Устанавливает cookie с токеном |
| `remove_token_cookie(response)` | Удаляет cookie |

**Структура токена:**
```
Header:  {"alg": "HS256", "typ": "JWT"}
Payload: {"user_id": int, "exp": int, "iat": int}
Signature: HMAC-SHA256(base64(header) + "." + base64(payload), secret_key)
```

**Особенности безопасности:**
- Жёстко закодированный алгоритм (не из заголовка токена)
- Проверка срока действия (`exp`)
- HTTP-only cookies
- SameSite cookies

### UserAuthService (`app/services/user_auth_service.py`)

| Метод | Назначение |
|---|---|
| `register_user(login, password)` | Регистрация: генерация дискриминатора, хеширование пароля, создание пользователя |
| `authenticate(login, password, discriminator=None)` | Аутентификация: поиск по login+discriminator, проверка пароля |
| `verify_password(password, password_hash)` | Проверка пароля (заглушка, сравнение в открытом виде) |
| `hash_password(password)` | Хеширование пароля (заглушка) |

**⚠️ ВАЖНО:** Пароли хранятся в открытом виде. Необходимо реализовать хеширование (bcrypt/argon2).

### PostService (`app/services/post_service.py`)

| Метод | Назначение |
|---|---|
| `create_post(user_id, title, body)` | Создание поста с валидацией |
| `get_post(post_id)` | Получение поста по ID |
| `get_all_posts()` | Все посты (сортировка по дате убывания) |
| `get_user_posts(user_id)` | Посты конкретного пользователя |
| `update_post(post_id, user_id, title, body)` | Обновление с проверкой авторства |
| `delete_post(post_id, user_id)` | Удаление с проверкой авторства (админ может удалить любой) |

### CommentService (`app/services/comment_service.py`)

| Метод | Назначение |
|---|---|
| `add_comment(post_id, user_id, body)` | Добавление комментария |
| `get_comments(post_id)` | Комментарии к посту |
| `update_comment(comment_id, user_id, body)` | Обновление с проверкой авторства |
| `delete_comment(comment_id, user_id)` | Удаление с проверкой авторства |

### CSRFService (`app/services/csrf_service.py`)

⚠️ **В разработке.** Заглушка возвращает `temp_csrf_token`.

### LoginAttemptService (`app/services/login_attempt_service.py`)

Защита от брутфорса на уровне приложения (дополнительно к Flask-Limiter):

| Метод | Назначение |
|---|---|
| `record_attempt(identifier, success)` | Запись попытки входа |
| `is_blocked(identifier)` | Проверка блокировки (5 неудачных попыток → блокировка на 15 минут) |
| `get_remaining_attempts(identifier)` | Оставшиеся попытки |
| `reset_attempts(identifier)` | Сброс после успешного входа |
| `cleanup_old_attempts()` | Очистка старых записей |

**Таблица БД:** `login_attempts` (identifier, attempt_time, success)

### RoleService (`app/services/role_service.py`)

| Метод | Назначение |
|---|---|
| `get_user_roles(user_id)` | Список ролей пользователя |
| `assign_role(user_id, role_name)` | Назначить роль |
| `remove_role(user_id, role_name)` | Снять роль |
| `is_admin(user_id)` | Проверка роли admin |
| `is_moderator(user_id)` | Проверка роли moderator |

**Паттерны:**
- **Service Layer** — бизнес-логика, изолированная от HTTP
- **Strategy** — разные алгоритмы хеширования
- **Dependency Injection** — сервисы получают репозитории через конструктор

---

## 8. Представления (`app/views/`)

Blueprints Flask, обрабатывающие HTTP-запросы. Не содержат бизнес-логики — только вызовы сервисов и рендеринг шаблонов.

### auth_bp (`app/views/auth.py`) — префикс `/auth`

| Маршрут | Методы | Ограничения | Назначение |
|---|---|---|---|
| `/auth/register` | GET, POST | 5/час | Регистрация нового пользователя |
| `/auth/login` | GET, POST | 10/мин | Вход (многоэтапный) |
| `/auth/select-account` | GET, POST | — | Выбор аккаунта при нескольких совпадениях логина |
| `/auth/logout` | GET, POST | — | Выход (удаление cookies) |

**Этапы входа (`/auth/login`):**
1. Поиск пользователей по логину через `UserRepository.find_by_login(login)`
2. Если один пользователь — проверка пароля и вход
3. Если несколько (одинаковый логин, разные дискриминаторы) — перенаправление на `/auth/select-account`
4. Если ни одного — ошибка аутентификации
5. Запись попытки через `LoginAttemptService`
6. Установка cookies: `jwt_token`, `remember_token`, `last_login`, `last_full_login`

**Особенности:**
- Поддержка `remember_me` (30 дней)
- Сохранение нескольких аккаунтов в cookies (JSON: `last_full_login`, `last_login`)
- Авто-вход после регистрации

### blog_bp (`app/views/blog.py`) — префикс `/`

| Маршрут | Методы | Авторизация | Назначение |
|---|---|---|---|
| `/` | GET | — | Список постов |
| `/post/<id>` | GET | — | Детальный просмотр поста |
| `/post/create` | GET, POST | Требуется | Создание поста |
| `/post/<id>/edit` | GET, POST | Автор или admin | Редактирование поста |
| `/post/<id>/delete` | POST | Автор или admin | Удаление поста |
| `/post/<id>/comment` | POST | Требуется | Добавление комментария |
| `/comment/<id>/delete` | POST | Автор или admin | Удаление комментария |

**Паттерны:**
- **Controller (MVC)** — обработка HTTP-запросов
- **Blueprint** — модульность Flask-приложения
- **Decorator** — `@login_required`, ограничения через `@limiter.limit`

---

## 9. Аутентификация (`app/auth.py`)

Middleware для JWT-авторизации.

**Функции:**

| Функция | Назначение |
|---|---|
| `load_user_from_token()` | `before_request` хук: извлекает токен из cookies, верифицирует, загружает пользователя в `g` |
| `login_required(view_func)` | Декоратор для защиты маршрутов |
| `get_current_user()` | Возвращает текущего пользователя из `g` |
| `get_current_user_id()` | Возвращает ID текущего пользователя |

**Процесс авторизации:**
1. Извлечение токена из cookies (`jwt_token` или `remember_token`)
2. Верификация через `JWTService.verify_token()`
3. Поиск пользователя через `UserRepository.find_by_id()`
4. Сохранение в `g.current_user` и `g.current_user_id`

---

## 10. CLI (`app/cli.py`)

Пользовательские команды Flask CLI.

| Команда | Назначение |
|---|---|
| `flask migrate` | Применить все неприменённые миграции |
| `flask migrate-upgrade` | Обновить схему БД |
| `flask seed` | Наполнить БД тестовыми данными |
| `flask db-reset` | Полный сброс и пересоздание БД |
| `flask create-admin` | Создать администратора |

**Паттерн:** Command Pattern — каждая CLI-команда инкапсулирует операцию.

---

*Документация создана на основе анализа исходного кода, май 2026.*