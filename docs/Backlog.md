# Backlog

Список будущих задач проекта. Подход к реализации выбирается при взятии задачи в работу.
Выполненные задачи фиксируются в [`CHANGELOG.md`](CHANGELOG.md) и из этого файла удаляются.

Синхронизация с [GitHub Project «Flask Blog»](https://github.com/users/discipleartem/projects/6): `python ~/.cursor/skills/backlog-github-projects-sync/scripts/sync_backlog.py` (конфиг [`.github/backlog.json`](../.github/backlog.json)).

Приоритеты доски (single select **Priority**): **`P0`** (критично) · **`P1`** (важно) · **`P2`** (низкий / продукт). Статусы: см. [GITHUB-PROJECTS-API.md](GITHUB-PROJECTS-API.md) и [backlog-status.mdc](../.cursor/rules/backlog-status.mdc).

Каждая задача — заголовок `## …` (одна GitHub Issue). Подзадачи — чеклисты внутри секции. Категория — поле `**Категория:**`.

---

## SEO: Open Graph / Twitter Card превью ссылок на статьи

**Статус:** in_progress
**GitHub:** #67
**Приоритет:** P2
**Категория:** UI / SEO

### Проблема

При вставке URL статьи в Telegram, Discord, Slack, VK и т.п. не показывается карточка сайта: в `<head>` нет `og:*` / `twitter:*` (только `<title>`). Краулеры не из чего собрать превью.

### Acceptance criteria

- Страница `/posts/<id>` отдаёт `og:title`, `og:description`, `og:url`, `og:type`, `og:image` (абсолютные URL) и базовые Twitter Card теги.
- Description — plain-text excerpt из `body_source` (reuse `plain_excerpt`).
- `og:image`: первое абсолютное изображение из Markdown тела, иначе дефолтная картинка сайта в `static/`.
- Unit-тесты: meta-теги присутствуют в HTML ответа detail.
- Кратко задокументировано в DEVELOPMENT / ARCHITECTURE.

### Подзадачи

- [x] Meta-теги в `posts/detail.html` (+ при необходимости site-level на главной)
- [x] Хелпер первого image URL из Markdown; дефолтный `og-default` asset
- [x] Unit-тесты
- [x] Docs

---

## Auth: CSRF на все mutating POST

**Статус:** open
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

- [ ] CSRF на CRUD постов
- [ ] CSRF на CRUD комментариев
- [ ] CSRF на admin users CRUD
- [ ] Logout перевести на POST + CSRF (убрать GET-logout или оставить redirect-only без side-effect)

---

## Auth: безопасный redirect `next` после login

**Статус:** open
**GitHub:** #55
**Приоритет:** P0
**Категория:** Auth / Security

### Проблема

После login используется `redirect(next_url)` без валидации — риск open redirect. Нужны только relative path / same-host.

### Acceptance criteria

- `next` принимается только если это безопасный относительный путь (или same-host URL по явной политике).
- Внешние и `//…` URL отклоняются; fallback на безопасный default (например home).
- Unit-тесты на допустимые и недопустимые значения `next`.

### Подзадачи

- [ ] Хелпер валидации `next` (whitelist relative)
- [ ] Подключить в login view
- [ ] Тесты open-redirect negatives

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

## Ops: безопасные дефолты SECRET_KEY / ADMIN_PASSWORD

**Статус:** open
**GitHub:** #60
**Приоритет:** P0
**Категория:** Ops / Deploy security

### Проблема

Дефолты `SECRET_KEY="dev-change-me"` и `ADMIN_PASSWORD="admin"` опасны при забытом `.env` на проде.

### Acceptance criteria

- В non-debug / production режиме приложение отказывается стартовать с известными небезопасными дефолтами **или** явно логирует hard fail.
- DEPLOY.md напоминает обязательность `.env`.
- Локальный dev с дефолтами по-прежнему удобен.

### Подзадачи

- [ ] Guard при старте factory (prod)
- [ ] Обновить DEPLOY.md / DEVELOPMENT.md
- [ ] Тест на отказ с bad defaults в prod-like config

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
