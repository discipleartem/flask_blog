# 🛠️ Разработка Flask Blog

**Версия:** 0.1.0 | **Дата:** Май 2026

---

## Оглавление

1. [Установка и запуск](#1-установка-и-запуск)
2. [Make-команды](#2-make-команды)
3. [Тестирование](#3-тестирование)
4. [Качество кода](#4-качество-кода)
5. [План развития (TODO)](#5-план-развития-todo)

---

## 1. Установка и запуск

### Предварительные требования

- Python 3.12 (версия по умолчанию; минимум `>=3.12` в `pyproject.toml`)
- `make` (опционально)

### Установка

```bash
# 1. Клонирование репозитория
git clone git@github.com:discipleartem/flask_blog.git
cd flask_blog

# 2. Создание виртуального окружения
python3.12 -m venv .venv
source .venv/bin/activate

# 3. Установка зависимостей
make install-dev

# 4. Инициализация БД
make migrate
make seed  # опционально
```

### Запуск

```bash
# Разработка (с автоперезагрузкой)
make dev

# Или напрямую
flask --app app run --debug

# Production
flask --app app run --host=0.0.0.0 --port=5000
```

### Переменные окружения (`.env`)

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///blog.db
PORT=5000
```

### Конфигурационные классы

| Класс | Назначение | Особенности |
|---|---|---|
| `Config` | Базовая | Загрузка из `os.getenv()`, значения по умолчанию |
| `DevelopmentConfig` | Разработка | `DEBUG=True` |
| `ProductionConfig` | Продакшн | `DEBUG=False`, `SESSION_COOKIE_SECURE=True`, логи в `logs/blog.log` |
| `TestingConfig` | Тестирование | `TESTING=True`, SQLite в памяти, CSRF отключён |

Доступ к конфигурациям через словарь `config`:
```python
from app.config import config
app = create_app(config['production'])
```

### Зависимости (pyproject.toml)

**Основные:**
- `Flask>=3.0.0` — веб-фреймворк
- `Flask-WTF>=1.2.0` — формы и CSRF
- `WTForms>=3.1.0` — библиотека форм
- `python-dotenv>=1.0.0` — загрузка `.env`
- `pysqlite3-binary>=0.5.0` — SQLite драйвер
- `Flask-Limiter>=3.5.0` — rate limiting

**Для разработки:**
- `pytest>=7.0.0` — тестирование
- `pytest-cov>=4.0.0` — покрытие
- `black>=23.0.0` — форматирование
- `ruff>=0.1.0` — линтинг
- `mypy>=1.0.0` — проверка типов
- `pre-commit>=3.0.0` — pre-commit хуки

---

## 2. Make-команды

| Команда | Назначение |
|---|---|
| `make help` | Показать все доступные команды |
| `make install-dev` | Установить зависимости для разработки |
| `make test` | Запустить тесты |
| `make test-cov` | Запустить тесты с покрытием (HTML-отчёт в `htmlcov/`) |
| `make code-quality` | Проверка кода: ruff → black → ruff format → mypy |
| `make migrate` | Применить миграции БД |
| `make migrate-up` | Обновить схему БД |
| `make seed` | Наполнить БД тестовыми данными |
| `make db-reset` | Полный сброс БД (удаление, пересоздание, миграции, seed) |
| `make clean` | Очистить временные файлы (`*.pyc`, `__pycache__`, `.pytest_cache`, etc.) |

---

## 3. Тестирование

### Запуск

```bash
# Все тесты
make test

# С покрытием
make test-cov

# Конкретный тест
pytest tests/test_basic.py -v

# С фильтрацией
pytest -k "test_name_pattern"
```

### Конфигурация тестирования

`TestingConfig` — специальный конфиг для тестов:
- `TESTING=True` — включает режим тестирования Flask
- `DATABASE_URL=sqlite:///:memory:` — БД в памяти (изолированные тесты)
- `WTF_CSRF_ENABLED=False` — CSRF отключён

### Конфигурация pytest (pyproject.toml)

```toml
[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --strict-markers --strict-config"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

### Маркеры

- `@pytest.mark.slow` — медленные тесты
- `@pytest.mark.integration` — интеграционные тесты

### Покрытие (coverage)

```toml
[tool.coverage.run]
source = ["app"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
]
```

---

## 4. Качество кода

### Инструменты

| Инструмент | Назначение | Конфигурация |
|---|---|---|
| **black** | Форматирование | `line-length=79`, `target-version=py312` |
| **ruff** | Линтинг + isort + pyupgrade | Правила: E, W, F, I, B, C4, UP |
| **mypy** | Проверка типов | Строгий режим (`disallow_untyped_defs=True`) |

### Запуск

```bash
# Все проверки одной командой
make code-quality

# Или по отдельности:
ruff check .
black .
ruff format .
mypy .
```

### Правила ruff

Включённые группы правил:
- `E` — pycodestyle errors
- `W` — pycodestyle warnings
- `F` — pyflakes
- `I` — isort (сортировка импортов)
- `B` — flake8-bugbear
- `C4` — flake8-comprehensions
- `UP` — pyupgrade

Игнорируемые правила:
- `E501` — длина строки (обрабатывает black)
- `B008` — вызовы функций в аргументах по умолчанию
- `C901` — слишком сложная функция

### Настройки mypy

```toml
[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true
```

---

## 5. План развития (TODO)

См. также [flask-blog-plan.md](flask-blog-plan.md) для полного плана.

### Приоритетные задачи

| # | Задача | Приоритет | Статус |
|---|---|---|---|
| 1 | ⚠️ **Хеширование паролей** — заменить открытое хранение на bcrypt/argon2 | Критический | ❌ |
| 2 | 🛡️ **CSRF-защита** — завершить реализацию CSRFService и middleware | Высокий | 🚧 В разработке |
| 3 | 📧 **Восстановление пароля** — email-подтверждение и сброс | Средний | ❌ |
| 4 | 📝 **Черновики постов** — статусы (draft/published) | Средний | ❌ |
| 5 | 🏷️ **Теги/категории** — система тегов для постов | Средний | ❌ |
| 6 | 🔍 **Поиск** — полнотекстовый поиск по постам | Средний | ❌ |
| 7 | 📄 **Пагинация** — серверная пагинация списка постов | Средний | ❌ |
| 8 | 🧪 **Увеличение покрытия тестами** — unit + integration тесты | Средний | ❌ |
| 9 | 🐳 **Docker** — контейнеризация приложения | Низкий | ❌ |
| 10 | 📊 **Админ-панель** — интерфейс управления пользователями и контентом | Низкий | ❌ |

### Рефакторинг и улучшения

- [ ] Вынести чистую архитектуру в `src/` (заготовка уже создана)
- [ ] Добавить pre-commit хуки
- [ ] Настроить CI/CD (GitHub Actions)
- [ ] Улучшить логирование (структурированные логи)
- [ ] Добавить кеширование (Redis/Memcached)
- [ ] API endpoints (REST API)

---

*Документация создана на основе анализа исходного кода, май 2026.*