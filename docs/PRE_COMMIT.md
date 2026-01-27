# Pre-commit Hook для Flask Блога

## Настройка

В проекте настроен автоматический pre-commit hook, который запускает проверки качества кода перед каждым коммитом.

## Какие проверки выполняются

1. **Black** - форматирование кода
2. **Flake8** - проверка стиля кода (только критические ошибки)
3. **Bandit** - проверка безопасности
4. **Pytest** - запуск тестов с покрытием кода

## Как работает

- Hook автоматически запускается при `git commit`
- Проверяются только измененные файлы в директории `app/` (тесты исключены)
- Если любая проверка не проходит, коммит отменяется
- Тесты требуют покрытия кода не менее 80%

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

# Стиль кода
source .venv/bin/activate && flake8 app/

# Безопасность
source .venv/bin/activate && bandit -r app/

# Тесты
source .venv/bin/activate && pytest tests/
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

### Тесты не проходят:
```bash
source .venv/bin/activate && pytest tests/ -v
```

### Bandit нашёл проблемы с безопасностью:
Исправьте уязвимости или добавьте `# nosec` комментарий, если это ложное срабатывание.

## Конфигурация

- **Pre-commit**: `.pre-commit-config.yaml`
- **Black**: `pyproject.toml` (секция `[tool.black]`)
- **Flake8**: `.flake8`
- **MyPy**: `pyproject.toml` (секция `[tool.mypy]`)
- **Bandit**: `pyproject.toml` (секция `[tool.bandit]`)
- **Pytest**: `pyproject.toml` (секция `[tool.pytest.ini_options]`)
