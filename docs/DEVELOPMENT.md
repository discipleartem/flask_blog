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
| Рендер | `app/content_render.py`, Jinja-фильтры `render_content`, `plain_excerpt` | Markdown / plain / html → nh3 → `Markup`. Extensions: `fenced_code`, `tables` (GFM), `nl2br`, `sane_lists`. Лента и `og:description`: `plain_excerpt` — краткий plain-text из `body_source` (строки GFM-таблиц `| … |` и markdown-картинки отбрасываются). `first_markdown_image_url` — первое абсолютное `http(s)` изображение для `og:image`. Без `| safe` по сырой колонке из БД |
| Social preview | `posts/index.html`, `posts/detail.html` | Open Graph + Twitter Card: title/description/url/image (абсолютные URL). Image: картинка из тела поста или `static/img/og-default.jpg` |
| Редактор | `app/static/js/markdown-editor.js`, vendor EasyMDE | JS обязателен для форм; чтение витрины без JS |
| Preview | `POST /markdown/preview` | Тот же `render_to_html`, что на витрине; кнопка «глаз» в тулбаре |
| Код | `app/static/js/syntax-highlight.js`, стили в `app.css` | Подсветка `pre code.language-*`: python, html, javascript, css, bash (+ aliases); иначе generic. Автоотступы (табы→пробелы, структурный indent); на submit — `formatMarkdownFences` |
| Таблицы | стили в `app.css` (`.post-body table`, EasyMDE preview) | GFM `| col |` → `<table>`; Bootstrap reboot без `.table` — границы/thead/zebra через scoped CSS на витрине и в preview |

Тулбар «Блок кода»: пресеты Python / HTML / JS / CSS / Bash или свой язык (` ```lang `).

На витрине и в preview у блоков кода две кнопки копирования (форматирование пробелов/отступов сохраняется):

- иконка «листы» — plain text;
- **MD** — fenced Markdown (` ```lang ` + код + ` ``` `).

Уведомление: тост «… скопирован в буфер»; на кнопке кратко галочка.

## UI / UX

**Bootstrap 5 — канон.** Сетка, навбар, формы, кнопки, alerts, collapse, spacing — через компоненты и utility-классы BS5.

Custom CSS (`app/static/css/app.css`) и JS (`theme.js`, `markdown-editor.js`, `syntax-highlight.js`) — **только исключения**: токены светлой/тёмной темы, бренд-типографика (IBM Plex), градиент hero, переключатель `data-bs-theme`, EasyMDE, подсветка/копирование кода, стили GFM-таблиц в `.post-body` / preview. Не дублировать layout Bootstrap своими правилами и не подключать другие CSS-фреймворки.

**Темы (чтение day/night):** light — тёплый paper/beige фон и мягкий графит; dark — gunmetal / metallic chrome и soft off-white. Токены `--fb-*` в `app.css`; `btn-dark` перекрашен под палитру. Приоритет — контраст и комфорт длинного чтения (`.post-body`), не чистый ч/б.

**Лента / пост / комментарии:** главная — surface-карточки (`.feed-item`), заголовок → excerpt (`plain_excerpt`) → мета; карточка целиком — ссылка на пост. Страница поста — reading column (`.post-body`: абзацы, списки, blockquote, GFM-таблицы). Комментарии — отдельные карточки (`.comment-item`) с `gap`, не плоский список с `border-bottom`.

**Админ-панель:** `/admin/` (только `is_admin`) — обзор + таблицы пользователей и статей; комментарии с авторами — drill-down `/admin/posts/<id>/comments` (текст через `render_content` + `syntax-highlight.js`). Вкладка **Модули** (`/admin/modules`) — каталог по категориям (Хостинг, Медиа, Локализация, Аккаунт); [PythonAnywhere](https://www.pythonanywhere.com/) в «Хостинг» (`/admin/modules/pythonanywhere`): username, API host, token и чекбоксы метрик **только из формы**; выбранные GET ([API](https://help.pythonanywhere.com/pages/API/)) на Dashboard в секции «Мониторинг». Таблица `pa_module_settings`. Edit/delete контента — маршруты `users` / `posts` / `comments`. Навбар: «Админка». Шаблоны: `app/templates/admin/`.

### Mobile / tablet first

1. Базовая разметка — для phone.
2. Усиление на `md` (планшет) и `lg`+ (ПК / wide) утилитами BS (`py-md-4`, `navbar-expand-lg`, …).
3. Контейнер: `container-fluid` + `px-3/px-md-4/px-xl-5` — без узкого `container-xxl`, контент использует ширину ПК / wide.
4. Sticky footer: `min-vh-100` + `flex-grow-1` на `main` (утилиты BS в `base.html`); sticky navbar (`sticky-top` + blur surface).
5. Переключатель темы — **вне** collapse на mobile/tablet (слева от hamburger); на desktop (`lg+`) — слева от «Войти» / действий пользователя.
6. Два экземпляра кнопки темы в разметке; JS вешается на все `.theme-toggle` (`app/static/js/theme.js`).
7. Active `nav-link` по `request.endpoint` / `request.blueprint`.
8. В шаблонах доступен `current_year` (context processor в `create_app`) — для футера.

## Git / ветки

Integration: `dev`. Релиз: `main`. Task-ветки: `feat/…`, `docs/…`, …

После merge PR **не удалять** ветку на GitHub без архива: переименовать в `merged/<имя>` локально и на `origin`, затем **checkout `dev`** (канон: [`.cursor/rules/git-merged-branches.mdc`](../.cursor/rules/git-merged-branches.mdc) + skill [`flask-blog-git-merged-archive`](../.cursor/skills/flask-blog-git-merged-archive/SKILL.md)).

## Проверка

**Автоматически (агент / CI):** только unit-тесты.

Локально:

```bash
source .venv/bin/activate
python -m unittest discover -s tests -v
```

В GitHub Actions: [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) на `push`/`pull_request` в `main` и `dev`. Деплой на PythonAnywhere ([`deploy.yml`](../.github/workflows/deploy.yml)) на `main` идёт только после успешного того же прогона.

**Вручную в браузере** (по необходимости, в т.ч. auth / password manager): регистрация → **Save** на ключике с полным `name#NNNN` → logout (`POST` с CSRF из навбара; `GET /auth/logout` сессию не чистит) → login через предложение браузера (autofill). Агент не гоняет Playwright/CDP-скрипты для этого.

**Сессия (TTL):** `Config.PERMANENT_SESSION_LIFETIME` — явный срок permanent-cookie (дефолт 30 дней, override `PERMANENT_SESSION_LIFETIME_DAYS`). Login без чекбокса «Запомнить меня» — не permanent (до закрытия браузера); с чекбоксом или сразу после register — permanent. См. `app/config.py`, `login_user(..., remember=…)`.

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

**Verify на показ:** пользователь хочет **видеть мышь** в окне Chrome — только headed, реальные клики IronBee (не headless / не «тихий» HTTP-only, если идёт UI-прогон). Rule: [`.cursor/rules/browser-verify-mouse.mdc`](../.cursor/rules/browser-verify-mouse.mdc).

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
   Расширение **всегда** перезаписывает `.cursor/rules/ironbee-devtools-use.mdc` (шаблон из `ironbee-ai.ironbee-devtools-vscode`; настройки «не писать» нет). Файл в `.gitignore`. Канон policy агента — [`00-project.mdc`](../.cursor/rules/00-project.mdc) §Verify; каталоги tools — в MCP.
4. По желанию — ручная проверка UI через IronBee или обычный Chrome (см. **Проверка** выше).

На Ubuntu с AppArmor (`apparmor_restrict_unprivileged_userns`) Playwright часто не может сам запустить Chromium — CDP к системному Chrome обходит это.

Если понадобится bundled Chromium (без CDP):

```bash
npx -y playwright@1.60.0 install chromium
```

Mobile/tablet: `interaction_resize-viewport` в том же окне Chrome.

## Структура / auth / права

Карта модулей, маршрутов, схемы БД и прав: [ARCHITECTURE.md](ARCHITECTURE.md). Вход агента: [`../AGENTS.md`](../AGENTS.md).

Локальные пути IDE (не в архитектурной карте): `.vscode/settings.json` (IronBee CDP, interpreter), `launch.json`, `terminal-init.sh`.

## Конфиг / секреты

Локально удобны дефолты `SECRET_KEY=dev-change-me` и `ADMIN_PASSWORD=admin` — они **разрешены** при debug (`flask --app wsgi run --debug` выставляет `FLASK_DEBUG=1` до factory).

В **non-debug** (WSGI на PA, `flask` без `--debug`, `FLASK_DEBUG=0`) те же значения → hard fail (`RuntimeError` + critical в лог). На проде всегда заполняйте `.env` (см. [DEPLOY.md](DEPLOY.md) §`.env`).

## Миграции

Файлы в `migrations/` применяются по имени (сортировка). Таблица `schema_migrations` хранит уже применённые файлы. SoT таблиц: [`schema.sql`](../schema.sql).

```bash
flask --app wsgi db-upgrade
```

Миграции также запускаются при `create_app()`. Для `db-upgrade` без `--debug` либо задайте секреты в `.env`, либо временно `FLASK_DEBUG=1`.
