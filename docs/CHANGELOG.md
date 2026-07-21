# Changelog

Все значимые изменения проекта фиксируются в этом файле.

Формат близкий к [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/).
Версии — [Semantic Versioning](https://semver.org/lang/ru/).

## [Unreleased]

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
