# Flask Blog

Веб-приложение блога на Flask — многопользовательская платформа с возможностью публикации постов и обсуждений.

## Технологический стек

* **Backend:** Python 3.13, Flask 3.0.3
* **Database:** SQLite (чистый SQL без ORM)
* **Frontend:** Bootstrap 5 (Jinja2 templates)
* **Инструменты:** Pytest (для тестирования)

## Структура проекта

    flask_blog/
    ├── app/
    │   ├── static/                 # Статические файлы (CSS, JS, изображения)
    │   ├── templates/
    │   │   ├── auth/
    │   │   │   ├── login.html      # Страница входа
    │   │   │   └── register.html   # Страница регистрации
    │   │   ├── base.html           # Базовый шаблон
    │   │   └── index.html          # Главная страница
    │   ├── __init__.py             # Фабрика приложения
    │   ├── auth.py                 # Blueprint аутентификации
    │   ├── config.py               # Конфигурация приложения
    │   ├── db.py                   # Работа с базой данных
    │   └── schema.sql              # SQL-схема базы данных
    ├── docs/
    │   └── BlogPlatformDevelopmentPlan.md  # План разработки
    ├── instance/                   # Файлы экземпляра (БД)
    ├── .gitignore
    ├── pyproject.toml
    ├── README.md
    └── requirements.txt

## Требования

* Python 3.13 или выше

## Установка

1. Клонируйте репозиторий:

        git clone <repository-url>
        cd flask_blog

2. Создайте виртуальное окружение и активируйте его:

        python -m venv .venv
        
        # Для Linux/macOS:
        source .venv/bin/activate
        
        # Для Windows:
        .venv\Scripts\activate

3. Установите зависимости:

        pip install -r requirements.txt

   Для разработки (включая pytest):

        pip install -e ".[dev]"

## Инициализация базы данных

Перед первым запуском необходимо создать таблицы в базе данных:

    flask --app app init-db

## Запуск приложения

    flask --app app run --debug

Приложение будет доступно по адресу: http://127.0.0.1:5000

## Особенности аутентификации

Система регистрации использует подход Discord:

* Логин **не уникален** — можно выбрать любой, даже если он занят
* Каждому пользователю присваивается уникальный тег (дискриминатор), например: `Username#1234`
* Для входа используется полный логин с тегом: `Username#1234`