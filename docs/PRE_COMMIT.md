# Pre-commit Hook для Flask Блога

## Настройка

В проекте настроен кастомный pre-commit hook, который автоматически запускает проверки качества кода перед каждым коммитом.

## Какие проверки выполняются

1. **Black** - форматирование кода
2. **Flake8** - проверка стиля кода (только критические ошибки)
3. **MyPy** - проверка типов
4. **Bandit** - проверка безопасности
5. **Pytest** - запуск тестов
6. **Coverage** - проверка покрытия кода ≥80%

## Как работает

- Hook автоматически запускается при `git commit`
- Проверяются только измененные файлы в директории `app/` (тесты исключены)
- Если любая проверка не проходит, коммит отменяется
- Тесты требуют покрытия кода не менее 80%
- Используется Python 3.13
- Генерируются JSON и HTML отчеты о покрытии

## 🚀 Инструкция по настройке Pre-commit Hook

### Шаг 1: Клонируйте репозиторий
```bash
git clone <repository-url>
cd flask_blog
```

### Шаг 2: Создайте виртуальное окружение
```bash
python -m venv .venv
source .venv/bin/activate
```

### Шаг 3: Установите зависимости
```bash
pip install -e ".[dev]"
```

### Шаг 4: Проверьте наличие hook файла
Убедитесь, что файл `.git/hooks/pre-commit` существует и является исполняемым:
```bash
ls -la .git/hooks/pre-commit
# Должен быть executable (rwxr-xr-x)
```

### Шаг 5: Если hook отсутствует, создайте его
```bash
# Скопируйте из шаблона или создайте вручную
cp .git/hooks/pre-commit.sample .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Шаг 6: Проверьте работу hook
```bash
# Сделайте тестовое изменение
echo "# Test" >> app/__init__.py
git add app/__init__.py

# Попробуйте коммит (должен запуститься hook)
git commit -m "Test pre-commit hook"
```

### Шаг 7: Отмените тестовое изменение
```bash
git reset --hard HEAD~1
```

## 📋 Запуск проверок вручную

### Запустить все проверки для всех файлов:
```bash
source .venv/bin/activate && .git/hooks/pre-commit
```

### Запустить конкретную проверку:
```bash
# Форматирование
source .venv/bin/activate && black app/

# Стиль кода (критические ошибки)
source .venv/bin/activate && flake8 --select=E9,F63,F7,F82 app/

# Проверка типов
source .venv/bin/activate && mypy app/ --ignore-missing-imports

# Безопасность
source .venv/bin/activate && bandit -r app/ --severity-level medium --confidence-level medium

# Тесты с покрытием
source .venv/bin/activate && pytest tests/ --cov=app --cov-report=json --cov-report=term-missing

# Проверка покрытия
python -c "import json; print(f'Coverage: {json.load(open(\"coverage.json\"))[\"totals\"][\"percent_covered\"]}%')"
```

## 🔄 Пропуск проверок (не рекомендуется)

Если необходимо пропустить проверки:
```bash
git commit --no-verify -m "Commit message"
```

## 🛠️ Устранение проблем

### Black нашёл проблемы с форматированием:
```bash
source .venv/bin/activate && black app/
git add . && git commit -m "Fix formatting"
```

### Flake8 нашёл проблемы со стилем:
```bash
source .venv/bin/activate && flake8 app/
# Исправьте ошибки вручную или настройте .flake8
```

### MyPy нашёл проблемы с типами:
```bash
source .venv/bin/activate && mypy app/ --ignore-missing-imports
# Добавьте аннотации типов или # type: ignore
```

### Тесты не проходят:
```bash
source .venv/bin/activate && pytest tests/ -v --cov=app --cov-report=json
```

### Покрытие кода ниже 80%:
```bash
# Посмотрите детальный отчет
open htmlcov/index.html
# или
python -c "import json; data=json.load(open('coverage.json')); print(f'Coverage: {data[\"totals\"][\"percent_covered\"]}%')"
```

### Bandit нашёл проблемы с безопасностью:
```bash
source .venv/bin/activate && bandit -r app/ --severity-level medium --confidence-level medium
# Исправьте уязвимости или добавьте # nosec
```

## ⚙️ Конфигурация

### Pre-commit Hook: `.git/hooks/pre-commit`
- Кастомный bash-скрипт
- Запускает проверки в последовательности
- Использует виртуальное окружение `.venv`

### Black: `pyproject.toml`
```toml
[tool.black]
line-length = 88
target-version = ['py313']
skip-string-normalization = false
```

### Flake8: `.flake8`
```ini
[flake8]
max-line-length = 88
exclude = .venv,__pycache__,*.pyc,.git,.pytest_cache,htmlcov,.coverage,.mypy_cache,.tox,build,dist
```

### MyPy: `pyproject.toml`
```toml
[tool.mypy]
python_version = "3.13"
ignore_missing_imports = true
```

### Bandit: `pyproject.toml`
```toml
[tool.bandit]
exclude_dirs = ["tests", ".venv", "__pycache__"]
severity = "medium"
confidence = "medium"
skips = ["B101"]
```

### Pytest: `pyproject.toml`
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["--tb=short", "--cov=app", "--cov-report=term-missing", "--cov-report=json", "--cov-report=html"]
cov-fail-under = 80
```

## 📦 Зависимости

Все инструменты установлены через `pyproject.toml`:
```toml
[project.optional-dependencies]
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

## 🔍 Troubleshooting

### Hook не запускается:
1. Проверьте права доступа: `chmod +x .git/hooks/pre-commit`
2. Убедитесь что файл существует: `ls .git/hooks/pre-commit`
3. Проверьте виртуальное окружение: `source .venv/bin/activate`

### Проблемы с путями:
1. Убедитесь что вы в корне проекта
2. Проверьте что `.venv` существует
3. Активируйте окружение: `source .venv/bin/activate`

### Проблемы с GitHub Actions:
1. Убедитесь что `coverage.json` генерируется
2. Проверьте путь в `.github/workflows/ci.yml`
3. Сравните локальные и CI команды

## 🎯 Лучшие практики

1. **Всегда исправляйте ошибки перед коммитом**
2. **Не используйте `--no-verify` без крайней необходимости**
3. **Следите за покрытием кода - держите ≥80%**
4. **Проверяйте HTML отчет покрытия: `open htmlcov/index.html`**
5. **Запускайте проверки вручную перед большими изменениями**
