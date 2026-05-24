---
name: flask-blog-mvp
overview: MVP блог-платформа на Python 3.12 + Flask + SQLite с чистым SQL, кастомной авторизацией на дескриминаторе Discord (без email) и простым черно-белым UI на Bootstrap 5.
todos:
  - id: cleanup-dependencies
    content: Удалить Flask-Login и Flask-SQLAlchemy, оставить только Flask, python-dotenv, Werkzeug.
    status: completed
  - id: setup-python-312
    content: Установить Python 3.12 из PPA deadsnakes, обновить pyproject.toml и пересоздать виртуальное окружение.
    status: completed
  - id: create-jwt-service
    content: Создать JWTService с самописным JWT (без алгоритма в header), поддержкой 24ч/30дней и HttpOnly cookies.
    status: completed
  - id: db-schema-migrations
    content: Спроектировать схему БД (users, posts, comments, migrations) и реализовать самописную систему миграций на чистом SQL с системой ролей и CLI для создания админа.
    status: completed
  - id: app-factory-and-db-layer
    content: Реализовать app factory `create_app()`, подключение к SQLite и минимальный слой доступа к данным (execute/fetch helpers).
    status: completed
  - id: discord-auth-service
    content: Реализовать `DiscordAuthService` с регистрацией (логин + дискриминатор + пароль), генерацией дискриминатора, хэшированием пароля и JWT токенами.
    status: completed
  - id: service-layer-blog
    content: Реализовать `PostService` и `CommentService` с CRUD-операциями и выборкой постов/комментариев с пользователями.
    status: completed
  - id: views-and-routing
    content: Реализовать blueprints `auth` и `blog` с маршрутами для регистрации/логина/логаута и CRUD постов/комментариев, включая главную страницу с группировкой постов по пользователям.
    status: completed
  - id: jwt-auth-middleware
    content: Создать декоратор `@login_required` и middleware для проверки JWT токенов в HttpOnly cookies.
    status: completed
  - id: csrf-and-guards
    content: Добавить минимальную CSRF-защиту для HTML-форм и декоратор `login_required` для защищённых маршрутов.
    status: pending
  - id: ui-templates
    content: Создать шаблоны Jinja2 с Bootstrap 5, базовым чёрно-белым стилем и mobile-first вёрсткой для главной, логина/регистрации, форм постов и комментариев.
    status: pending
  - id: basic-tests
    content: Написать базовые тесты на миграции, JWT авторизацию и CRUD постов/комментариев для проверки работоспособности MVP.
    status: pending
isProject: false
---

# План реализации MVP блог-платформы на Flask

## 🚫 Важные ограничения и требования

- **PythonAnywhere**: Redis НЕ поддерживается даже на платных тарифах
- **Авторизация**: Только логин + дискриминатор + пароль (без email)
- **БД**: Чистый SQL без ORM, SQLite
- **JWT**: Самописный JWT с HttpOnly cookies (stateless)
- **Python 3.12**: Последняя версия с улучшениями производительности
- **Менторский подход**: Объясняю, направляю, НЕ пишу код

## 1. Базовая структура проекта и окружение

- **✅ Python 3.12**: Установлен из PPA deadsnakes, виртуальное окружение создано
- **✅ Зависимости**: Flask, python-dotenv, Werkzeug (очищены от Flask-Login)
- **Структура проекта**: `app/` (ядро), `app/views/` (контроллеры), `app/services/` (сервисный слой), `app/repositories/` (SQL-репозитории), `app/models/` (DTO), `migrations/`, `app/templates/`, `app/static/`.
- **Настройки**: `config.py` с `.env` (SECRET_KEY, ADMIN_PASSWORD, DATABASE_URL)

## 2. Самописный JWT сервис (безопасный подход)

- **JWTService**: Самописная реализация на `hmac` + `hashlib`
- **Безопасность**: Алгоритм НЕ хранится в токене, жестко закодирован в коде
- **Срок жизни**: 24 часа стандартно, 30 дней с "запомнить меня"
- **Хранение**: HttpOnly cookies, SameSite=Lax, Secure=True в production
- **Структура токена**: Payload с `user_id`, `exp`, `iat` (минимум данных)

## 3. База данных и миграции (SQLite + чистый SQL)

- **Схема БД**:
  - `users`: `id`, `login`, `discriminator`, `password_hash`, `created_at`, `updated_at`
  - `roles`: `id`, `name`, `description`, `created_at`
  - `user_roles`: `user_id`, `role_id`, `assigned_at` (many-to-many)
  - `posts`: `id`, `user_id`, `title`, `body`, `created_at`, `updated_at`
  - `comments`: `id`, `post_id`, `user_id`, `body`, `created_at`, `updated_at`
  - `migrations`: `id`, `name`, `applied_at`
- **Уникальность**: Композитный уникальный constraint на `(login, discriminator)` для пользователей
- **Система ролей**: Гибкая система с таблицами `roles` и `user_roles`
- **Самописные миграции**: `migrations/migration_runner.py` с нумерованными SQL-файлами
- **CLI команды**: `flask migrate`, `flask rollback`, `flask create-admin`
- **ВАЖНО**: Таблица `sessions` НЕ нужна (используем JWT stateless)

## 4. Flask-приложение, MVC и сервисный слой

- **App factory**: `create_app()` в `app/__init__.py`
- **Repository Layer**: `app/repositories/user_repo.py`, `post_repo.py`, `comment_repo.py` с чистым SQL
- **Service Layer**:
  - `JWTService`: генерация и проверка JWT токенов
  - `DiscordAuthService`: регистрация, логин, работа с JWT
  - `PostService`, `CommentService`: CRUD операции
- **Models**: `User`, `Post`, `Comment` как DTO классы

## 5. Кастомная авторизация на дескриминаторе Discord + JWT

### Регистрация:
1. Пользователь вводит `login` и `password`
2. Проверяем, что `login` не зарезервирован ('admin')
3. Генерируется случайный `discriminator` (4 цифры)
4. Проверяется уникальность пары `(login, discriminator)`
5. Пароль хэшируется через `werkzeug.security`

### Особенности admin:
- Логин 'admin' зарезервирован системой
- `discriminator = NULL` в БД
- Не отображается дискриминатор в UI

### Логин и JWT:
1. Пользователь вводит `login` и `password`
2. Находим пользователя по `login` (без дискриминатора)
3. Проверяем пароль
4. Генерируем JWT токен через `JWTService`
5. Устанавливаем `HttpOnly` cookie с токеном

### Механизм "запомнить меня":
- Браузер автозаполняет форму с логином
- Для обычных пользователей требуется выбор дискриминатора при логине
- Admin логинится по логину 'admin' без дискриминатора

## 6. JWT Middleware и декораторы

- **JWTService**: `generate_token()`, `verify_token()`, `_create_signature()`
- **@login_required**: Декоратор для защиты маршрутов
- **Middleware**: Проверка JWT в cookies для каждого запроса
- **g.current_user**: Установка текущего пользователя из JWT

## 7. Блог-функциональность

- **Главная страница**: посты сгруппированные по пользователям
- **CRUD постов**: только для авторизованных, редактирование автору/админу
- **CRUD комментариев**: авторизованным, редактирование автору/админу
- **Валидация**: базовая проверка обязательных полей

## 8. UI/UX: Bootstrap 5, черно-белая тема, mobile-first

- **Базовый шаблон `base.html`**:
  - Bootstrap 5 через CDN
  - Черно-белая палитра
  - Навбар с ссылками для авторизованных/неавторизованных
- **Формы авторизации**:
  - Поле для логина и пароля
  - Если несколько пользователей с одинаковым логином - показать выбор дискриминатора
  - Admin логинится без дискриминатора
- **Адаптивность**: mobile-first подход

## 9. Запуск, тестирование и развертывание

- **PythonAnywhere особенности**:
  - Нет Redis, используем JWT stateless
  - Запуск через WSGI, не `flask run`
  - Статические файлы через `/static/`
- **Минимальные тесты**:
  - Миграции БД
  - JWT генерация/проверка
  - CRUD операций
- **Развертывание**:
  - Настройка WSGI на PythonAnywhere
  - Переменные окружения через web-интерфейс

## 🎯 Ключевые технические решения

### Безопасный JWT (без алгоритма в header):
```python
class JWTService:
    ALGORITHM = "HS256"  # Жестко закодировано!
    
    def generate_token(self, user_id: int, remember_me: bool = False) -> str:
        # Header не храним, используем только ALGORITHM из кода
        # Payload: {"user_id": 123, "exp": timestamp, "iat": timestamp}
        # Signature: HMAC-SHA256(secret_key, payload)
```

### Структура репозиториев:
```python
# app/repositories/user_repo.py
class UserRepository:
    def find_by_login_and_discriminator(self, login: str, discriminator: str) -> Optional[User]:
        # SQL: SELECT * FROM users WHERE login = ? AND discriminator = ?
        
    def find_by_login(self, login: str) -> List[User]:
        # SQL: SELECT * FROM users WHERE login = ?
        
    def find_by_id(self, user_id: int) -> Optional[User]:
        # SQL: SELECT * FROM users WHERE id = ?
        
    def find_admin(self) -> Optional[User]:
        # SQL: SELECT u.* FROM users u 
        # JOIN user_roles ur ON u.id = ur.user_id 
        # JOIN roles r ON ur.role_id = r.id 
        # WHERE r.name = 'admin'
        
    def is_login_reserved(self, login: str) -> bool:
        # Проверка зарезервированных логинов (admin)
        return login.lower() in ['admin']
        
    def create_user(self, user: User) -> int:
        # SQL: INSERT INTO users (login, discriminator, password_hash) VALUES (?, ?, ?)
        
    def assign_role(self, user_id: int, role_name: str) -> bool:
        # SQL: INSERT INTO user_roles (user_id, role_id) 
        # VALUES (?, (SELECT id FROM roles WHERE name = ?))
```

### JWT Middleware:
```python
@app.before_request
def load_user_from_jwt():
    token = request.cookies.get('auth_token')
    if token:
        payload = jwt_service.verify_token(token)
        if payload:
            g.current_user = user_repo.find_by_id(payload['user_id'])
```

## 🎯 Статус реализации

### ✅ Выполненные задачи:
1. **cleanup-dependencies** - Удалены лишние зависимости, оставлен только Flask
2. **setup-python-312** - Python 3.12 установлен и настроен
3. **create-jwt-service** - JWTService реализован с самописным JWT
4. **db-schema-migrations** - Полная система миграций с ролями и CLI

### 🔄 Текущие задачи:
- **csrf-and-guards** - CSRF защита для форм
- **ui-templates** - Bootstrap 5 интерфейс с шаблонами
- **basic-tests** - Тестирование функциональности MVP

### 📋 Архитектурные решения:
- **Система ролей**: Гибкая many-to-many связь с таблицами roles и user_roles вместо is_admin флага
- **Репозитории**: Repository Pattern с чистым SQL и GROUP_CONCAT для загрузки ролей
- **Модели**: Dataclass с property methods для работы с ролями (is_admin, has_role)
- **Миграции**: Самописная система с логированием и откатом
- **JWT**: HttpOnly cookies, stateless авторизация
- **БД**: Чистый SQL без ORM, SQLite
- **CLI**: Flask команды для управления

