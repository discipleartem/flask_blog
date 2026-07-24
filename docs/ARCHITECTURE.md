# Architecture

Плотная карта для scoping. Howto — в [DEVELOPMENT.md](DEVELOPMENT.md) / [DEPLOY.md](DEPLOY.md). SoT схемы SQL: [`schema.sql`](../schema.sql).

## Слои

| Слой | Где |
|------|-----|
| Entry | `wsgi.py` → `create_app()` |
| Factory | `app/__init__.py` — blueprints, `before_request`, фильтр `render_content`, CSRF в context |
| Blueprints | `app/auth`, `posts`, `comments`, `users`, `deploy` |
| Данные | `app/db.py` + SQLite (`Config.DATABASE`) |
| UI | Jinja `app/templates/` + Bootstrap 5; static исключения в `app/static/` |

## Маршруты

| Method | Path | Blueprint |
|--------|------|-----------|
| GET, POST | `/auth/register` | auth |
| GET | `/auth/register/success` | auth |
| GET, POST | `/auth/login` | auth |
| GET | `/auth/logout` | auth |
| GET | `/` | posts |
| GET | `/posts/<id>` | posts |
| GET, POST | `/posts/new` | posts |
| GET, POST | `/posts/<id>/edit` | posts |
| POST | `/posts/<id>/delete` | posts |
| POST | `/markdown/preview` | posts |
| POST | `/posts/<id>/comments` | comments |
| GET, POST | `/comments/<id>/edit` | comments |
| POST | `/comments/<id>/delete` | comments |
| GET | `/users/` | users |
| GET | `/users/<id>` | users |
| GET, POST | `/users/<id>/edit` | users |
| POST | `/users/<id>/delete` | users |
| POST | `/internal/deploy` | deploy |

## Данные

| Таблица | Ключевые поля |
|--------|----------------|
| `users` | `name`, `discriminator`, `password_hash`, `is_admin` |
| `posts` | `title`, `body_source`, `body_format`, `author_id` |
| `comments` | `post_id`, `user_id`, `body_source`, `body_format` |
| `schema_migrations` | `filename`, `applied_at` |

`body_format`: `plaintext` \| `markdown` \| `html`. Формы Post/Comment пишут `markdown`. Индексы и FK — в `schema.sql`. Миграции: `migrations/*.sql` через `run_migrations()` / `flask db-upgrade`.

## Поток запроса

1. `before_request`: `load_logged_in_user` → `g.user` из `session["user_id"]` (или `None`).
2. Шаблоны: `csrf_token`, `current_year` (context processor).
3. Контент на витрине: фильтры `render_content` / `plain_excerpt` (`app/content_render.py` + nh3), не сырой `| safe` из БД. Страницы `/` и `/posts/<id>`: Open Graph / Twitter Card meta (`og:*`, `twitter:*`); description из `plain_excerpt`, image — `first_markdown_image_url` или `static/img/og-default.jpg`.
4. Login: cookie session; без JWT. Deploy-hook: Bearer `DEPLOY_SECRET` (не user-auth).

## Права

| Действие | Автор | Admin |
|----------|-------|-------|
| Свои посты/комментарии CRUD | да | да |
| Чужие посты/комментарии | нет | да |
| Список / правка / удаление пользователей | нет | да (не последнего admin) |

Identity: `name#NNNN`. Имя `admin` зарезервировано. Seed: `admin#0001`.

## Карта `app/`

| Путь | Назначение |
|------|------------|
| `__init__.py` | App factory |
| `config.py` | Config + `.env` |
| `db.py` | sqlite3 helpers, миграции |
| `content_render.py` | Markdown/plain/html → безопасный HTML (в т.ч. GFM tables); `plain_excerpt` / `first_markdown_image_url` для ленты и OG |
| `csrf.py` | CSRF token helpers |
| `auth/` | register/login/logout + helpers |
| `posts/` | лента, CRUD постов, markdown preview, OG meta на index/detail |
| `comments/` | CRUD комментариев |
| `users/` | профиль + admin CRUD |
| `deploy/` | `POST /internal/deploy` |
| `templates/` | Jinja + Bootstrap 5 |
| `static/css/app.css` | тема, бренд, код-блоки (исключения сверх BS5) |
| `static/js/` | `theme.js`, `markdown-editor.js`, `syntax-highlight.js` |
| `static/img/` | `og-default.jpg` — fallback для `og:image` |
| `static/vendor/easymde/` | EasyMDE (не CDN) |

Корень репо (рядом): `schema.sql`, `migrations/`, `tests/`, `wsgi.py`, `.github/workflows/`.
