# Changelog

Все значимые изменения проекта фиксируются в этом файле.

Формат близкий к [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/).
Версии — [Semantic Versioning](https://semver.org/lang/ru/).

## [Unreleased]

### Added

- Open Graph / Twitter Card meta на `/` и `/posts/<id>` (`og:title`, `og:description`, `og:url`, `og:image`, `twitter:*`); fallback-картинка `static/img/og-default.jpg`; `first_markdown_image_url` в `content_render`.
- Jinja-фильтр `plain_excerpt` (`app/content_render.py`) — краткий plain-text превью для ленты постов.

### Changed

- UI: тёплая paper/beige дневная и gunmetal/chrome ночная темы; sticky nav с active links; комфорт чтения (`.post-body`); формы и users без `table-light` / лишних `shadow-sm`.
- UI: комментарии на странице поста — отдельные surface-карточки с `gap` и акцентной левой границей (читаемее в light/dark).
- UI: лента на главной — карточки статей с иерархией заголовок → excerpt → мета и hover, вместо плоского `list-group`.
- UI: чтение средней статьи — ритм абзацев/списков, blockquote на surface; в ленте clamp заголовка и excerpt до 3 строк (карточка целиком — ссылка на пост).

### Fixed

- GFM markdown tables: границы/thead/zebra в `.post-body` и EasyMDE preview (`app.css`); extension `tables` уже был в `content_render`.
- Лента: `plain_excerpt` больше не показывает сырые `| col |` строки GFM-таблиц.

### Docs

- `docs/GITHUB-PROJECTS-API.md`: возможности Projects v2, GraphQL/REST/`gh`, маппинг Status/Priority на backlog.
- Backlog: auth/security задачи из обзора (CSRF, `next`, rate limit, session, пароли, prod defaults) с Priority P0–P2; sync → issues #54–#61 на Project «Flask Blog».
- `backlog.json` / `backlog-status.mdc`: поле Priority; статус `ready` убран из `statusMap`.
- Backlog #51 (обновление дизайна warm/chrome UI) выполнен и удалён из `Backlog.md` после merge в `dev`.
- Skill `flask-blog-git-release-sync`: синхронизация `dev` ← `main` после релиза (конфликты CHANGELOG/version — в пользу `main`).
- DEVELOPMENT §UI / §Контент, ARCHITECTURE и `ui-bootstrap.mdc`: warm/chrome dual theme, лента/комментарии, фильтр `plain_excerpt`.
- Gate: skill `flask-blog-docs-after-task` обязателен перед PR task → `dev` (порядок docs → verify → push → PR); обновлены `00-project`, `docs-context`, `backlog-status`, `task-cycle`, `git-commit-pr`.
- DEVELOPMENT §Контент: GFM tables + scoped CSS; Backlog #63 выполнен и удалён из `Backlog.md` после merge в `dev`.
- DEVELOPMENT §Контент: Open Graph / Twitter Card; Backlog #67 выполнен и удалён из `Backlog.md` после merge в `dev`.
- Post-merge: skill `flask-blog-git-merged-archive` — docs/backlog cleanup PR сразу squash-merge в том же turn (не оставлять открытый `docs/*-backlog-done`); обновлены `backlog-status.mdc`, `git-merged-branches.mdc`.

## [0.3.0] — 2026-07-21

### Added

- Markdown для Post/Comment: `body_source` + `body_format`, EasyMDE (vendor), серверный рендер (`content_render` + nh3), `POST /markdown/preview`.
- Подсветка кода на витрине (`syntax-highlight.js`: python/html/js/css/bash), автоотступы fenced-блоков, кнопки копирования plain и Markdown с тостом.
- GitHub Actions CI: unit-тесты (Python 3.12) на `push`/`pull_request` в `main` и `dev` (`.github/workflows/ci.yml`).
- Deploy на PythonAnywhere gated: job `deploy` после успешного `test` в `.github/workflows/deploy.yml`.
- Страница успешной регистрации с полным логином `name#NNNN` и сохранением учётки через Credential Management API (`PasswordCredential`), чтобы менеджер паролей предлагал полный тег, а не только имя без дискриминатора.
- Регистрация через `fetch` (XHR), чтобы Chrome не предлагал сохранить неполный username из HTML-формы.
- Unit-тесты на страницу успеха регистрации и поле входа `username`.
- Задача backlog по UI auth / password manager; правило переходов статусов backlog (`in_progress` → `in_review` → `done`).

### Fixed

- После регистрации в той же сессии навбар видит пользователя: `login_user` выставляет `g.user` без редиректа.
- Вход согласован с autofill браузера: поле `name="username"`, сервер принимает `username`.
- В сохранённую учётку попадает только полный логин `name#NNNN`.

### Changed

- Автопроверка агента: только `unittest`; сценарий password manager (Save на ключике → logout → login через предложение браузера) — ручная проверка в браузере.

### Docs

- Backlog #47 (Обновление документации) закрыт после merge в `dev` (#48).
- Рефакторинг Cursor rules/skills (context engineering): slim alwaysApply (IronBee policy в `00-project`, docs-context scoping-only); удалён `flask-blog-workflow.mdc`; skill `flask-blog-git-merged-archive`; mapping docs только в `flask-blog-docs-after-task`; сужены globs `auth`/`database`; `backlog-status` / `git-merged-branches` не alwaysApply. `ironbee-devtools-use.mdc` — артефакт расширения (`.gitignore`), не править вручную.
- Docs-first карта для экономии токенов: `AGENTS.md` (роутер), `docs/README.md`, `docs/ARCHITECTURE.md`; правило `docs-context.mdc`; дедуп структуры/прав из `DEVELOPMENT.md` (backlog #47).
- Skill `flask-blog-docs-after-task` + hook `stop`: автозапуск обновления docs в конце реализации.
- Тематические rules (`flask-3`, `auth`, `database`, …) ссылаются на ARCHITECTURE вместо дублей карт/прав; алгоритмы scoping — в `docs-context.mdc` / AGENTS.
- Backlog #44 (Markdown-редактор) закрыт после merge в `dev` (#45).
- `DEVELOPMENT.md`: контент Markdown (рендер, preview, подсветка, копирование кода), структура `content_render` / static JS.
- `SESSION_COOKIE_SECURE` для HTTPS-деплоя (`.env.example`, `DEPLOY.md`).
- Уточнён приоритет окружения над `.env` при `load_dotenv` (уже заданные переменные процесса не перезаписываются).
- В `DEVELOPMENT.md` — политика unit-тестов и ручной проверки auth UI.
- После merge task-ветки на GitHub не удалять: переименовать в `merged/*` (правило + skill `flask-blog-git-merged-archive`).

## [0.2.0] — 2026-07-19

### Added

- Bootstrap 5 mobile-first UI (канон разметки; custom CSS/JS только для темы и бренда).
- Секреты через `.env` / `.env.example`, `python-dotenv`.
- Auto-deploy на PythonAnywhere при push в `main` (GitHub Actions + endpoint `/internal/deploy`).
- Расширенная документация деплоя и разработки; настройки IronBee DevTools.

### Changed

- Шаблоны auth / posts / comments / users переведены на компоненты Bootstrap 5.

## [0.1.0] — 2026-07-18

### Added

- MVP: session-аутентификация `username#discriminator`, статьи и плоские комментарии.
- SQLite (raw SQL), `schema.sql`, самописные миграции.
- Один admin (`admin#0001`), светлая/тёмная тема.
- Unit-тесты (`unittest`), docs по деплою на PythonAnywhere.
