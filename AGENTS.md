# AGENTS — роутер контекста

Цель: **меньше токенов**. Сначала этот файл → 1–2 docs → точечные пути в коде. Не сканировать репозиторий «на всякий случай».

## Порядок

1. Этот файл — выбрать **одну** строку таблицы ниже.
2. Открыть только указанные docs (и rule при необходимости).
3. Читать **только** перечисленные пути кода.
4. Карта модулей/маршрутов/схемы: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).
5. Индекс всех docs: [`docs/README.md`](docs/README.md).

Стек и запреты: [`.cursor/rules/00-project.mdc`](.cursor/rules/00-project.mdc).

## Тип задачи → что открыть

| Тип задачи | Docs / rules | Код | Не читать |
|------------|--------------|-----|-----------|
| Auth / session / identity | ARCHITECTURE §Права, `auth.mdc` | `app/auth/` | DEPLOY, IronBee, vendor |
| Посты / лента / preview | ARCHITECTURE §Маршруты, DEVELOPMENT §Контент | `app/posts/`, `app/content_render.py` | DEPLOY, `app/deploy/` |
| Комментарии | ARCHITECTURE, DEVELOPMENT §Контент | `app/comments/` | DEPLOY, users admin |
| Пользователи / профиль | ARCHITECTURE §Права, `auth.mdc` | `app/users/` | DEPLOY, markdown JS |
| Админ-панель `/admin/` | ARCHITECTURE §Маршруты/Права, `auth.mdc` | `app/admin/`, `app/templates/admin/` | DEPLOY, IronBee |
| БД / схема / миграции | ARCHITECTURE §Данные, `database.mdc` | `schema.sql`, `migrations/`, `app/db.py` | templates, static, DEPLOY |
| UI / шаблоны / тема | DEVELOPMENT §UI, `ui-bootstrap.mdc` | `app/templates/`, `app/static/css/`, `app/static/js/` | `vendor/easymde/` целиком, DEPLOY |
| Markdown-редактор / подсветка | DEVELOPMENT §Контент | `content_render.py`, `static/js/markdown-editor.js`, `syntax-highlight.js` | DEPLOY, auth |
| CSRF / config / factory | ARCHITECTURE §Поток | `app/__init__.py`, `app/csrf.py`, `app/config.py` | DEPLOY |
| Деплой / PA / hook | DEPLOY | `app/deploy/`, `.github/workflows/` | DEVELOPMENT UI, IronBee |
| Релиз / GitHub Release | RELEASE, github-releases-api | skills `flask-blog-git-release*`, `docs/CHANGELOG.md` | UI, IronBee, schema |
| Тесты | `testing.mdc` | `tests/` (+ модуль под тестом) | DEPLOY, static vendor |
| Backlog / статусы задач | `backlog-status.mdc`, Backlog.md | — | код приложения |
| Docs / карта проекта | этот файл, `docs/README.md` | `docs/`, `AGENTS.md`, `.cursor/rules/docs-context.mdc` | широкий `app/` |

## Запреты контекста

- Не читать: `.venv/`, `__pycache__/`, `app/static/vendor/` (кроме явного указания версии), полные минифицированные бандлы.
- Не запускать широкий explore / Task по всему `app/`, если строка таблицы уже дала пути.
- Не открывать весь `DEVELOPMENT.md` или `DEPLOY.md`, если задача не про них — достаточно секций по ссылкам/якорям.

## После изменения поведения

Skill [`.cursor/skills/flask-blog-docs-after-task/SKILL.md`](.cursor/skills/flask-blog-docs-after-task/SKILL.md): mapping «куда писать» + commit + backlog `in_review` (**обязательно до PR в `dev`**; hook `stop`). Scoping: [`.cursor/rules/docs-context.mdc`](.cursor/rules/docs-context.mdc). Не копировать карты ARCHITECTURE в rules.
