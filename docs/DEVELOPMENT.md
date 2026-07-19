# Development

## Стек (зафиксирован)

| Компонент | Версия | Примечание |
|-----------|--------|------------|
| Python | 3.12 | `.venv` |
| Flask | **3.0.3** | ограничение PythonAnywhere; не поднимать до 3.1+ |

Зависимости: [`pyproject.toml`](../pyproject.toml) (основной) и [`requirements.txt`](../requirements.txt) (для PA / `pip install -r`).

## Структура

```
app/
  __init__.py      # create_app
  config.py
  db.py            # sqlite3 helpers + migrations
  auth/            # register / login / logout
  users/           # profile + admin CRUD
  posts/           # feed + CRUD
  comments/        # CRUD
  templates/
  static/
migrations/        # numbered *.sql
schema.sql         # source of truth
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
