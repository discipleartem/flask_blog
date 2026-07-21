# Development

## Стек (зафиксирован)

| Компонент | Версия | Примечание |
|-----------|--------|------------|
| Python | 3.12 | `.venv` |
| Flask | **3.0.3** | ограничение PythonAnywhere; не поднимать до 3.1+ |
| Bootstrap | **5.3.x** | единственный UI-фреймворк; CDN в `base.html` |
| Markdown | Python-Markdown + nh3 | рендер/санитизация на сервере (`app/content_render.py`) |
| Редактор | EasyMDE **2.18.0** | vendor в `app/static/vendor/easymde/` (не CDN) |

Зависимости: [`pyproject.toml`](../pyproject.toml) (основной) и [`requirements.txt`](../requirements.txt) (для PA / `pip install -r`).

## Контент Post / Comment

| Поле | Смысл |
|------|--------|
| `body_source` | Канон — исходник автора |
| `body_format` | `plaintext` \| `markdown` \| `html` |

Формы Post/Comment сохраняют Markdown: сервер всегда пишет `body_format=markdown`, поле формы — `body_source` (клиентский `body_format` игнорируется). Миграция схемы: `migrations/002_content_body_fields.sql` (`body` → `body_source` + `body_format`).

| Слой | Файлы | Поведение |
|------|--------|-----------|
| Рендер | `app/content_render.py`, Jinja-фильтр `render_content` | Markdown / plain / html → nh3 → `Markup`. Без `| safe` по сырой колонке из БД |
| Редактор | `app/static/js/markdown-editor.js`, vendor EasyMDE | JS обязателен для форм; чтение витрины без JS |
| Preview | `POST /markdown/preview` | Тот же `render_to_html`, что на витрине; кнопка «глаз» в тулбаре |
| Код | `app/static/js/syntax-highlight.js`, стили в `app.css` | Подсветка `pre code.language-*`: python, html, javascript, css, bash (+ aliases); иначе generic. Автоотступы (табы→пробелы, структурный indent); на submit — `formatMarkdownFences` |

Тулбар «Блок кода»: пресеты Python / HTML / JS / CSS / Bash или свой язык (` ```lang `).

На витрине и в preview у блоков кода две кнопки копирования (форматирование пробелов/отступов сохраняется):

- иконка «листы» — plain text;
- **MD** — fenced Markdown (` ```lang ` + код + ` ``` `).

Уведомление: тост «… скопирован в буфер»; на кнопке кратко галочка.

## UI / UX

**Bootstrap 5 — канон.** Сетка, навбар, формы, кнопки, alerts, collapse, spacing — через компоненты и utility-классы BS5.

Custom CSS (`app/static/css/app.css`) и JS (`theme.js`, `markdown-editor.js`, `syntax-highlight.js`) — **только исключения**: токены светлой/тёмной темы, бренд-типографика (IBM Plex), градиент hero, переключатель `data-bs-theme`, EasyMDE, подсветка/копирование кода. Не дублировать layout Bootstrap своими правилами и не подключать другие CSS-фреймворки.

### Mobile / tablet first

1. Базовая разметка — для phone.
2. Усиление на `md` (планшет) и `lg`+ (ПК / wide) утилитами BS (`py-md-4`, `navbar-expand-lg`, …).
3. Контейнер: `container-fluid` + `px-3/px-md-4/px-xl-5` — без узкого `container-xxl`, контент использует ширину ПК / wide.
4. Sticky footer: `min-vh-100` + `flex-grow-1` на `main` (утилиты BS в `base.html`).
5. Переключатель темы — **вне** collapse на mobile/tablet (слева от hamburger); на desktop (`lg+`) — слева от «Войти» / действий пользователя.
6. Два экземпляра кнопки темы в разметке; JS вешается на все `.theme-toggle` (`app/static/js/theme.js`).
7. В шаблонах доступен `current_year` (context processor в `create_app`) — для футера.

## Git / ветки

Integration: `dev`. Релиз: `main`. Task-ветки: `feat/…`, `docs/…`, …

После merge PR **не удалять** ветку на GitHub без архива: переименовать в `merged/<имя>` локально и на `origin` (канон для агента: [`.cursor/rules/git-merged-branches.mdc`](../.cursor/rules/git-merged-branches.mdc)).

## Проверка

**Автоматически (агент / CI):** только unit-тесты.

Локально:

```bash
source .venv/bin/activate
python -m unittest discover -s tests -v
```

В GitHub Actions: [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) на `push`/`pull_request` в `main` и `dev`. Деплой на PythonAnywhere ([`deploy.yml`](../.github/workflows/deploy.yml)) на `main` идёт только после успешного того же прогона.

**Вручную в браузере** (по необходимости, в т.ч. auth / password manager): регистрация → **Save** на ключике с полным `name#NNNN` → logout → login через предложение браузера (autofill). Агент не гоняет Playwright/CDP-скрипты для этого.

## IronBee DevTools (опционально)

| Настройка | Значение | Смысл |
|-----------|----------|--------|
| `browser.headless` | `false` | не headless-shell |
| `browser.persistent` | `false` | обязательно `false` при CDP (иначе конфликт) |
| `browser.useSystemBrowser` | `true` | системный Chrome, не bundled Chromium |
| `browser.executablePath` | `/usr/bin/google-chrome` | путь к Chrome |
| `browser.cdp.enable` | `true` | отдельное окно системного Chrome |
| `browser.cdp.endpointUrl` | `http://127.0.0.1:9222` | CDP endpoint |
| `platform.browser.enable` | `true` | MCP browser |
| `platform.backend.enable` | `true` | HTTP / SQLite smoke |

### Быстрый старт

1. Flask: `flask --app wsgi run --debug` (порт 5000).
2. Отдельное окно Chrome с CDP (папка `scripts/` локальная, не в git):

```bash
PROFILE="${XDG_CACHE_HOME:-$HOME/.cache}/flask-blog-chrome-profile"
mkdir -p "$PROFILE"
google-chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="$PROFILE" \
  --no-first-run \
  --no-default-browser-check \
  --disable-sync \
  http://127.0.0.1:5000/
```

Опционально можно держать обёртку в локальном `scripts/dev-chrome.sh` (игнорируется git).

3. В Cursor: **Developer: Reload Window** (чтобы IronBee подхватил settings).
4. По желанию — ручная проверка UI через IronBee или обычный Chrome (см. **Проверка** выше).

На Ubuntu с AppArmor (`apparmor_restrict_unprivileged_userns`) Playwright часто не может сам запустить Chromium — CDP к системному Chrome обходит это.

Если понадобится bundled Chromium (без CDP):

```bash
npx -y playwright@1.60.0 install chromium
```

Mobile/tablet: `interaction_resize-viewport` в том же окне Chrome.

## Структура

```
app/
  __init__.py      # create_app (+ current_year, фильтр render_content)
  config.py        # load_dotenv(.env) + Config
  db.py            # sqlite3 helpers + migrations
  content_render.py  # Markdown/plain/html → nh3
  auth/            # register / login / logout
  users/           # profile + admin CRUD
  posts/           # feed + CRUD + POST /markdown/preview
  comments/        # CRUD
  deploy/          # POST /internal/deploy (Bearer DEPLOY_SECRET)
  templates/       # Bootstrap 5, mobile/tablet first
  static/
    css/app.css    # тема, бренд, hero, код-блоки — исключения сверх BS5
    js/theme.js    # data-bs-theme + .theme-toggle
    js/markdown-editor.js
    js/syntax-highlight.js
    vendor/easymde/
migrations/        # numbered *.sql
schema.sql         # source of truth
.env.example       # шаблон секретов (реальный .env в .gitignore)
.github/workflows/ # ci.yml (unittest); deploy.yml — push main → PA (после test)
.vscode/
  settings.json    # IronBee CDP, Python interpreter, terminal+venv
  launch.json      # debugpy → flask run
  terminal-init.sh # activate .venv в integrated terminal
tests/             # unittest
wsgi.py
```

## Миграции

Файлы в `migrations/` применяются по имени (сортировка). Таблица `schema_migrations` хранит уже применённые файлы.

```bash
flask --app wsgi db-upgrade
```

Миграции также запускаются при `create_app()`.

## Auth

- Cookie session (`user_id`), без JWT
- Идентичность: `name#discriminator` (4 цифры)
- Имя `admin` зарезервировано для регистрации
- Seed: `admin#0001` с `is_admin=1`

## Права

| Действие | Автор | Admin |
|----------|-------|-------|
| Свои посты/комментарии CRUD | да | да |
| Чужие посты/комментарии | нет | да |
| Список пользователей | нет | да |
| Удаление пользователей | нет | да (не последнего admin) |
