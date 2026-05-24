# Flask Blog

Простой блог на Flask с автоматической активацией виртуального окружения.

## 🚀 Быстрый старт

### 1. Создание виртуального окружения

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

### 2. Установка зависимостей

```bash
# Если окружение уже создано
make install

# Полная инициализация проекта
make init
```

### 3. Запуск приложения

```bash
# Через Makefile
make run

# Или напрямую
python run.py
```

## 📁 Структура проекта

```
flask_blog/
├── .venv/                 # Виртуальное окружение (Python 3.13)
├── .vscode/              # Настройки VS Code
│   ├── settings.json     # Автоматическая активация .venv
│   └── launch.json       # Конфигурации отладки
├── .windsurf/            # Настройки Windsurf IDE
│   ├── settings.json     # Автоматическая активация .venv
│   └── launch.json       # Конфигурации отладки
│   └── rules/            # Правила для AI ассистента
├── app/                  # Основное приложение
├── tests/                # Тесты
├── docs/                 # Документация
├── .env                  # Переменные окружения
├── pyproject.toml        # Управление зависимостями
├── Makefile             # Удобные команды
└── run.py               # Точка входа
```

## ⚙️ Конфигурация

### Windsurf IDE
- Автоматическая активация `.venv` в терминале
- Использование Python из `.venv/bin/python`
- Настроенные переменные окружения в `.windsurf/settings.json`

### VS Code (дополнительно)
- Автоматическая активация `.venv` в терминале
- Использование Python из `.venv/bin/python`
- Настроенные переменные окружения в `.vscode/settings.json`

### Flask
- Переменные окружения из `.env`
- Режим отладки по умолчанию

## 🔧 Доступные команды (Makefile)

```bash
make help        # Показать все команды
make init        # Полная инициализация проекта
make run         # Запустить приложение
make dev         # Запустить в режиме разработки
make test        # Запустить тесты
make lint        # Проверить код
make format      # Форматировать код
make clean       # Очистить временные файлы
```

## 🐍 Python 3.13

Проект использует Python 3.13:

```bash
# Проверка версии
python --version  # Должно быть Python 3.13.x

# Создание окружения
python3.13 -m venv .venv
```

## 📦 Зависимости

Основные:
- Flask >= 3.0.0
- Flask-WTF >= 1.2.0
- WTForms >= 3.1.0
- python-dotenv >= 1.0.0
- pysqlite3-binary >= 0.5.0

Для разработки:
- pytest, black, ruff, mypy

## 🗄️ База данных

Проект использует **чистый SQL** без ORM:
- Собственный слой доступа к данным в `app/db.py`
- SQL миграции в `app/migrations/`
- Data Transfer Objects в `app/models/`
- Репозитории в `app/repositories/`

## 🔄 Автоматическая активация в IDE

### Windsurf IDE (основная)
- Настроено в `.windsurf/settings.json`
- Автоматическая активация `.venv` при открытии терминала
- Использование Python из `.venv/bin/python`

### VS Code (дополнительная)
- Настроено в `.vscode/settings.json`
- Автоматическая активация `.venv` при открытии терминала
- Использование Python из `.venv/bin/python`

### Ручная активация (если нужно)

```bash
source .venv/bin/activate
```

## 🧪 Тестирование

```bash
# Все тесты
make test

# С покрытием
make test-cov

# Конкретный тест
pytest tests/test_app.py
```

## 📝 Разработка

```bash
# Режим разработки с автоперезагрузкой
make dev

# Форматирование кода
make format

# Проверка стиля
make lint

# Все проверки
make check
```

## 📄 Лицензия

MIT License