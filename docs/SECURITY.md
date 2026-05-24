# 🔒 Безопасность Flask Blog

**Версия:** 0.1.0 | **Дата:** Май 2026

---

## Оглавление

1. [JWT-авторизация](#1-jwt-авторизация)
2. [Брутфорс-защита](#2-брутфорс-защита)
3. [CSRF-защита](#3-csrf-защита)
4. [XSS-защита](#4-xss-защита)
5. [SQL-инъекции](#5-sql-инъекции)
6. [Cookies](#6-cookies)
7. [Дискриминаторы](#7-дискриминаторы)
8. [Резервирование логинов](#8-резервирование-логинов)

---

## 1. JWT-авторизация

### Реализация

**Самописный JWT-сервис** (`app/services/jwt_service.py`) без внешних библиотек. Алгоритм **HS256** жёстко закодирован в коде и не извлекается из заголовка токена (защита от атаки "algorithm confusion").

### Структура токена

```
Header:  {"alg": "HS256", "typ": "JWT"}
Payload: {"user_id": int, "exp": int, "iat": int}
Signature: HMAC-SHA256(base64(header) + "." + base64(payload), secret_key)
```

### Методы JWTService

| Метод | Назначение |
|---|---|
| `generate_token(user_id, duration=None)` | Создаёт JWT с payload `{user_id, exp, iat}`. По умолчанию 7 дней |
| `verify_token(token)` | Проверяет подпись (HMAC-SHA256) и срок действия (`exp`) |
| `decode_token(token)` | Извлекает payload без проверки подписи |
| `get_token_from_request()` | Извлекает токен из cookies: сначала `jwt_token`, затем `remember_token` |
| `set_token_cookie(response, token, duration)` | Устанавливает HttpOnly cookie |
| `remove_token_cookie(response)` | Удаляет cookie (выход) |

### Процесс авторизации (`app/auth.py`)

1. `before_request` хук `load_user_from_token()` вызывается для каждого запроса
2. Извлекает токен из cookies через `JWTService.get_token_from_request()`
3. Верифицирует токен через `JWTService.verify_token()`
4. Извлекает `user_id` из payload
5. Загружает пользователя через `UserRepository.find_by_id()`
6. Сохраняет в `g.current_user` и `g.current_user_id`

### Использование в маршрутах

```python
from app.auth import login_required, get_current_user

@blog_bp.route('/post/create', methods=['GET', 'POST'])
@login_required
def create_post():
    user = get_current_user()
    # ...
```

### Меры безопасности

- **Алгоритм жёстко закодирован** — не извлекается из заголовка токена
- **Проверка срока действия** — `exp` проверяется при каждой верификации
- **HTTP-only cookies** — токен недоступен из JavaScript
- **SameSite cookies** — защита от CSRF на уровне браузера
- **Secure cookies** — в production (`SESSION_COOKIE_SECURE=True`)

---

## 2. Брутфорс-защита

Два уровня защиты:

### Уровень 1: Flask-Limiter

Глобальные ограничения (инициализируются в `create_app()`):
```python
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)
```

По-маршрутные ограничения:
```python
@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per hour")     # 5 попыток регистрации в час

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")  # 10 попыток входа в минуту
```

### Уровень 2: LoginAttemptService

Сервис `app/services/login_attempt_service.py` — дополнительная защита на уровне приложения:

| Метод | Описание |
|---|---|
| `record_attempt(identifier, success)` | Записывает попытку в таблицу `login_attempts` |
| `is_blocked(identifier)` | Проверяет, заблокирован ли идентификатор |
| `get_remaining_attempts(identifier)` | Возвращает количество оставшихся попыток |
| `reset_attempts(identifier)` | Сбрасывает счётчик после успешного входа |
| `cleanup_old_attempts()` | Удаляет старые записи (старше 15 минут) |

**Логика блокировки:**
- 5 неудачных попыток → блокировка на 15 минут
- Идентификатор: IP-адрес или логин пользователя
- После успешного входа счётчик сбрасывается

### Интеграция в процесс входа

В `auth_bp.login()`:
1. Проверка `LoginAttemptService.is_blocked(identifier)` перед попыткой аутентификации
2. При неудаче: `LoginAttemptService.record_attempt(identifier, success=False)`
3. При успехе: `LoginAttemptService.reset_attempts(identifier)`

---

## 3. CSRF-защита

⚠️ **В разработке.**

Текущее состояние:
- `CSRFService` (`app/services/csrf_service.py`) — заглушка
- `inject_csrf_token()` context processor возвращает `'temp_csrf_token'`
- Middleware для проверки CSRF закомментирован в `create_app()`

**План реализации:**
1. Генерация токена на основе `SECRET_KEY` + `session_id`
2. Внедрение токена в формы через скрытое поле
3. Проверка токена для методов POST/PUT/DELETE через `before_request` middleware
4. Двойная отправка cookie (Double Submit Cookie Pattern)

---

## 4. XSS-защита

Реализована через механизмы Jinja2:

- **Автоэкранирование** — `{{ variable }}` автоматически экранирует HTML-сущности
- **Безопасный вывод** — `{{ variable|safe }}` используется осознанно только для доверенного контента
- **Фильтр `nl2br`** — преобразует `\n` в `<br>\n` без риска XSS (работает с уже экранированным текстом)

---

## 5. SQL-инъекции

Все запросы используют **параметризованные запросы** (placeholders `?`):

```python
# Безопасно — параметризованный запрос
db.execute_query("SELECT * FROM users WHERE login = ?", (login,), fetch_one=True)

# НЕ используется конкатенация строк
# db.execute_query(f"SELECT * FROM users WHERE login = '{login}'")  # ОПАСНО!
```

Функции `execute_query()`, `execute_insert()`, `execute_update()`, `execute_batch()` в `app/db.py` принимают параметры отдельно от SQL-строки.

---

## 6. Cookies

### Конфигурация

| Параметр | Значение | Описание |
|---|---|---|
| `SESSION_COOKIE_HTTPONLY` | `True` | Cookie недоступны из JavaScript |
| `SESSION_COOKIE_SAMESITE` | `'lax'` | Защита от CSRF |
| `SESSION_COOKIE_SECURE` | `True` (production) | Только HTTPS |
| `SESSION_COOKIE_DURATION` | 7 дней | Стандартная сессия |

### Используемые cookies

| Cookie | Назначение | HttpOnly | Срок |
|---|---|---|---|
| `jwt_token` | Основной токен авторизации | ✅ | 7 дней |
| `remember_token` | Токен «запомнить меня» | ✅ | 30 дней |
| `last_login` | Последний логин (для автозаполнения) | ❌ | 30 дней |
| `last_full_login` | Последний полный логин с дискриминатором | ❌ | 30 дней |
| `theme` | Тема оформления (light/dark) | ❌ | 365 дней |

---

## 7. Дискриминаторы

Система дискриминаторов позволяет создавать несколько аккаунтов с одинаковым логином:

- Формат: `login#1234` (4 цифры)
- Первый аккаунт с данным логином: `discriminator = NULL` (отображается просто как `login`)
- Последующие аккаунты: `discriminator` = 4-значный код (0001-9999)
- Уникальность: `UNIQUE(login, discriminator)` в таблице `users`
- Генерация: `UserRepository.generate_discriminator(login)` находит следующий свободный номер

**Защита от коллизий:**
- Дискриминатор генерируется как `MAX(discriminator) + 1` для данного логина
- Начинается с 0001 (если есть аккаунт с NULL, следующий получит 0001)
- Максимум 10000 аккаунтов на один логин (0000-9999, исключая NULL)

---

## 8. Резервирование логинов

Следующие логины зарезервированы и не могут быть использованы при регистрации:

`admin`, `moderator`, `system`, `root`, `owner`

Проверка выполняется в `UserRepository` при создании пользователя. Попытка использовать зарезервированный логин вызывает ошибку валидации.

---

*Документация создана на основе анализа исходного кода, май 2026.*