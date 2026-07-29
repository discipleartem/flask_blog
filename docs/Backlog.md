# Backlog

Список будущих задач проекта. Подход к реализации выбирается при взятии задачи в работу.
Выполненные задачи фиксируются в [`CHANGELOG.md`](CHANGELOG.md) и из этого файла удаляются.

Синхронизация с [GitHub Project «Flask Blog»](https://github.com/users/discipleartem/projects/6): `python ~/.cursor/skills/backlog-github-projects-sync/scripts/sync_backlog.py` (конфиг [`.github/backlog.json`](../.github/backlog.json)).

Приоритеты доски (single select **Priority**): **`P0`** (критично) · **`P1`** (важно) · **`P2`** (низкий / продукт). Статусы: см. [GITHUB-PROJECTS-API.md](GITHUB-PROJECTS-API.md) и [backlog-status.mdc](../.cursor/rules/backlog-status.mdc).

Каждая задача — заголовок `## …` (одна GitHub Issue). Подзадачи — чеклисты внутри секции. Категория — поле `**Категория:**`.

---

## Auth: CSRF на все mutating POST

**Статус:** in_review
**GitHub:** #54
**Приоритет:** P0
**Категория:** Auth / Security

### Проблема

CSRF-токен и `validate_csrf()` есть только на login/register. Формы постов, комментариев и users (create/edit/delete) без серверной проверки. Logout через GET без CSRF. `SameSite=Lax` смягчает риск, но не заменяет CSRF на state-changing endpoints.

### Acceptance criteria

- Все mutating POST (posts, comments, users) принимают и проверяют CSRF.
- Шаблоны форм содержат скрытое поле CSRF (или эквивалент).
- Unit-тесты: отказ без токена / с неверным токеном.

### Подзадачи

- [x] CSRF на CRUD постов
- [x] CSRF на CRUD комментариев
- [x] CSRF на admin users CRUD
- [x] Logout перевести на POST + CSRF (убрать GET-logout или оставить redirect-only без side-effect)

---

## Auth: rate limit / backoff на login

**Статус:** open
**GitHub:** #56
**Приоритет:** P1
**Категория:** Auth / Abuse prevention

### Проблема

`/auth/login` не ограничен — возможен brute-force по паролю.

### Acceptance criteria

- При серии неудачных попыток с одного IP (и/или login) включается задержка или временная блокировка.
- Успешный login сбрасывает счётчик для субъекта.
- Поведение задокументировано в DEVELOPMENT / ARCHITECTURE (кратко).

### Подзадачи

- [ ] Выбрать механизм (in-memory / SQLite bucket — без новой СУБД)
- [ ] Применить к login POST
- [ ] Unit-тесты на порог и сброс

---

## Auth: не грузить `password_hash` в `g.user`

**Статус:** open
**GitHub:** #57
**Приоритет:** P1
**Категория:** Auth / Hardening

### Проблема

`load_logged_in_user` делает `SELECT *`, поэтому `password_hash` оказывается в request context на каждый запрос (лишние данные; риск утечки в шаблоны при ошибке).

### Acceptance criteria

- Запрос пользователя для `g.user` не выбирает `password_hash`.
- Login по-прежнему читает хеш только в auth view.
- Существующие auth/unit-тесты зелёные.

### Подзадачи

- [ ] Явный список колонок в `load_logged_in_user`
- [ ] Проверить, что шаблоны/хелперы не зависят от лишних полей

---

## Auth: ужесточить политику пароля

**Статус:** open
**GitHub:** #58
**Приоритет:** P1
**Категория:** Auth / Hardening

### Проблема

Минимум 6 символов без требований к сложности / словарям.

### Acceptance criteria

- Задана явная политика (длина и/или классы символов) на register и смене пароля (если есть).
- Сообщения об ошибке не раскрывают лишнюю информацию о существующих пользователях.
- Unit-тесты на отказ слабых паролей.

### Подзадачи

- [ ] Правила валидации + константы/конфиг
- [ ] UI-подсказка в форме регистрации
- [ ] Тесты

---

## Auth: явный TTL сессии

**Статус:** open
**GitHub:** #59
**Приоритет:** P1
**Категория:** Auth / Session

### Проблема

`session.permanent = True` без явной политики TTL (дефолт Flask ~31 день). Нет разделения «remember me» vs короткий idle timeout.

### Acceptance criteria

- В config задан явный `PERMANENT_SESSION_LIFETIME` (или эквивалент).
- Поведение описано в docs (DEVELOPMENT / ARCHITECTURE).
- По возможности — опция короткой сессии без permanent (если UX позволит).

### Подзадачи

- [ ] Константа TTL в config
- [ ] Документация
- [ ] (Опционально) remember-me checkbox

---

## Auth (продукт): password reset / 2FA / роли

**Статус:** open
**GitHub:** #61
**Приоритет:** P2
**Категория:** Auth / Product

### Проблема

Нет сброса пароля, email-verify, 2FA; роль только `is_admin`. Для учебного блога ожидаемо; брать в работу только при реальной потребности.

### Acceptance criteria

- Перед реализацией — отдельное решение «нужно ли» (не делать «на будущее»).
- Если делается: минимальный вертикальный срез с тестами и docs.

### Подзадачи

- [ ] (Опционально) password reset flow
- [ ] (Опционально) 2FA
- [ ] (Опционально) роли шире admin/user — только с обоснованием
