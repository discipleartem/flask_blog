# Flask Blog

Блог на Flask 3 + Bootstrap 5 + SQLite (raw SQL), session-auth в стиле Discord (`username#0001`).

## Требования

- Python 3.12
- виртуальное окружение `.venv`

## Установка

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .
# или: pip install -r requirements.txt
```

## Запуск

```bash
source .venv/bin/activate
export FLASK_APP=wsgi:app
flask --app wsgi run --debug
```

По умолчанию:

- БД: `instance/blog.sqlite3`
- Admin: `admin#0001` / пароль из `ADMIN_PASSWORD` (по умолчанию `admin`)

```bash
export SECRET_KEY=change-me
export ADMIN_PASSWORD=strong-password
flask --app wsgi db-upgrade
```

## Тесты

```bash
source .venv/bin/activate
python -m unittest discover -s tests -v
```

## Документация

- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
- [docs/DEPLOY.md](docs/DEPLOY.md) — PythonAnywhere

## Project board

[Flask Blog (GitHub Projects)](https://github.com/users/discipleartem/projects/6/views/1)
