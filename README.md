# Flask Blog

Минималистичный блог на **Flask 3.0.3** (Python 3.12) с монохромным UI (Bootstrap 5), SQLite без ORM и session-аутентификацией в стиле Discord (`username#0001`).

Версия Flask зафиксирована под ограничения [PythonAnywhere](docs/DEPLOY.md): **Python 3.12 + Flask 3.0.3**.

[![Version 0.3.0](https://img.shields.io/badge/version-0.3.0-blue.svg)](docs/CHANGELOG.md)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Flask 3.0.3](https://img.shields.io/badge/flask-3.0.3-black.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)


**Репозиторий:** [discipleartem/flask_blog](https://github.com/discipleartem/flask_blog) · **Доска задач:** [Flask Blog](https://github.com/users/discipleartem/projects/6/views/1)

## Возможности

- Регистрация / вход без email: `name#discriminator` (успех регистрации + password manager)
- CRUD статей и плоских комментариев (автор — свои; admin — все)
- Markdown-редактор (EasyMDE), серверный рендер и preview; подсветка кода на витрине
- Один admin (`admin#0001`, имя `admin` зарезервировано)
- Светлая / тёмная тема (переключатель солнце / луна)
- Чистый SQL + `schema.sql` + самописные миграции
- CI (GitHub Actions) и авто-деплой на [PythonAnywhere](docs/DEPLOY.md)

## Стек

| Слой | Технология |
|------|------------|
| Runtime | Python 3.12, `.venv` |
| Web | Flask **3.0.3** (pin для PythonAnywhere) |
| UI | **Bootstrap 5.3** (mobile/tablet first); custom CSS/JS — только исключения |
| DB | SQLite3, raw SQL |
| Auth | Session cookie, `werkzeug.security` |
| Tests | `unittest` |

## Требования

- Python 3.12
- Flask 3.0.3 (не обновлять до 3.1+ — ограничение хостинга)
- Git

## Установка

```bash
git clone https://github.com/discipleartem/flask_blog.git
cd flask_blog
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .
# запасной вариант: pip install -r requirements.txt
cp .env.example .env
# заполните SECRET_KEY, ADMIN_PASSWORD (и при необходимости DATABASE)
```

## Запуск

```bash
source .venv/bin/activate
export FLASK_APP=wsgi:app
flask --app wsgi db-upgrade
flask --app wsgi run --debug
```

Откройте http://127.0.0.1:5000/

Секреты — в `.env` (шаблон: [`.env.example`](.env.example)). Уже экспортированные переменные окружения имеют приоритет над `.env`.

| Параметр | Значение по умолчанию |
|----------|------------------------|
| БД | `instance/blog.sqlite3` |
| Admin | `admin#0001` |
| Пароль admin | `ADMIN_PASSWORD` или `admin` |

## Тесты

```bash
source .venv/bin/activate
python -m unittest discover -s tests -v
```

## Документация

- [AGENTS.md](AGENTS.md) — вход для агента: тип задачи → docs → пути кода (экономия контекста)
- [docs/README.md](docs/README.md) — индекс документации
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — модули, маршруты, схема, права
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) — UI (Bootstrap 5), контент/Markdown, IronBee, проверки
- [docs/DEPLOY.md](docs/DEPLOY.md) — PythonAnywhere **Beginner**, `.env`, auto-deploy при push в `main`
- [docs/CHANGELOG.md](docs/CHANGELOG.md) — история изменений

## Ветки

| Ветка | Назначение |
|-------|------------|
| `main` | стабильный релиз |
| `dev` | интеграция |

## License

[MIT](LICENSE) © Tomas
