# Pre-commit Hook для Flask Блога

## Настройка

В проекте настроен автоматический pre-commit hook, который запускает проверки качества кода перед каждым коммитом.

## Какие проверки выполняются

1. **Black** - форматирование кода
2. **Flake8** - проверка стиля кода (только критические ошибки)
3. **MyPy** - проверка типов (строгий режим)
4. **Bandit** - проверка безопасности
5. **Pytest** - запуск тестов с покрытием кода ≥80%

## Как работает

- Hook автоматически запускается при `git commit`
- Проверяются только измененные файлы в директории `app/` (тесты исключены)
- Если любая проверка не проходит, коммит отменяется
- Тесты требуют покрытия кода не менее 80%
- Используется Python 3.13

## Запуск вручную

### Запустить все проверки для всех файлов:
```bash
source .venv/bin/activate && pre-commit run --all-files
```

### Запустить только для измененных файлов:
```bash
source .venv/bin/activate && pre-commit run
```

### Запустить конкретную проверку:
```bash
# Форматирование
source .venv/bin/activate && black app/

# Стиль кода (критические ошибки)
source .venv/bin/activate && flake8 --select=E9,F63,F7,F82 app/

# Проверка типов
source .venv/bin/activate && mypy app/ --strict

# Безопасность
source .venv/bin/activate && bandit -r app/ --severity-level medium --confidence-level medium

# Тесты
source .venv/bin/activate && pytest tests/ --cov=app --cov-fail-under=80
```

## Пропуск проверок (не рекомендуется)

Если необходимо пропустить проверки:
```bash
git commit --no-verify
```

## Устранение проблем

### Black нашёл проблемы с форматированием:
```bash
source .venv/bin/activate && black app/
```

### Flake8 нашёл проблемы со стилем:
Исправьте ошибки вручную или настройте `.flake8` файл.

### MyPy нашёл проблемы с типами:
```bash
source .venv/bin/activate && mypy app/ --strict
```
Добавьте аннотации типов или `# type: ignore` для ложных срабатываний.

### Тесты не проходят:
```bash
source .venv/bin/activate && pytest tests/ -v --cov=app
```

### Bandit нашёл проблемы с безопасностью:
Исправьте уязвимости или добавьте `# nosec` комментарий, если это ложное срабатывание.

## Конфигурация

- **Pre-commit Hook**: `.git/hooks/pre-commit` (кастомный bash-скрипт)
- **Black**: `pyproject.toml` (секция `[tool.black]`)
  - `target-version = ['py313']`
  - `line-length = 88`
- **Flake8**: `.flake8`
  - `max-line-length = 88`
  - `exclude = .venv,__pycache__,*.pyc,.git,.pytest_cache,htmlcov,.coverage,.mypy_cache,.tox,build,dist`
- **MyPy**: `pyproject.toml` (секция `[tool.mypy]`)
  - `python_version = "3.13"`
  - `strict = true`
- **Bandit**: `pyproject.toml` (секция `[tool.bandit]`)
  - `exclude_dirs = ["tests", ".venv", "__pycache__"]`
  - `severity = "medium"`
  - `confidence = "medium"`
- **Pytest**: `pyproject.toml` (секция `[tool.pytest.ini_options]`)
  - `testpaths = ["tests"]`
  - `cov-fail-under = 80`
  - `addopts = ["--tb=short", "--cov=app", "--cov-report=term-missing"]`

## Зависимости

Все инструменты установлены через `pyproject.toml` в секции `[project.optional-dependencies]`:
```toml
dev = [
    "pytest>=8.0.0",
    "pytest-flask>=1.3.0",
    "pytest-cov>=4.0.0",
    "black>=24.0.0",
    "flake8>=7.0.0",
    "mypy>=1.8.0",
    "bandit>=1.7.0",
    "pre-commit>=3.0.0",
]
```
