# Flask Blog

A simple blog application built with Flask framework that supports user authentication, article management, and commenting system.

## Features
- User registration and authentication
- Create, read, update and delete blog articles
- Comment system for articles
- SQLite database storage
- Simple and clean interface

## Tech Stack
- Python 3.13
- Flask 2.0.3
- Flask-Login 0.5.0
- Flask-WTF 0.15.1
- SQLite database
- JavaScript
- HTML/CSS

## Project Structure

```markdown
project/
├── app/
│   ├── forms/                      # Формы Flask-WTF
│   │   ├── __init__.py
│   │   ├── article_forms.py        # Форма для статей
│   │   ├── auth_forms.py           # Формы авторизации и регистрации
│   │   └── comment_form.py         # Форма комментариев
│   │
│   ├── models/                     # Модели данных
│   │   ├── __init__.py             # Экспорт моделей
│   │   ├── article.py              # Модель статьи
│   │   ├── comment.py              # Модель комментария
│   │   └── user.py                 # Модель пользователя
│   │
│   ├── routes/                     # Маршруты приложения
│   │   ├── article_routes.py       # Обработка статей
│   │   ├── auth_routes.py          # Авторизация и регистрация
│   │   └── comment_routes.py       # Обработка комментариев
│   │
│   ├── tests/                     # Тесты приложения
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit                        # Модульные тесты
│   │   ├── auth/
│   │   │   ├── test_forms.py
│   │   │   ├── test_models.py
│   │   │   └── test_routes.py
│   │   ├── article
│   │   │   ├── test_forms.py
│   │   │   ├── test_models.py
│   │   │   └── test_routes.py
│   │   └── comment
│   │       ├── test_forms.py
│   │       ├── test_models.py
│   │       └── test_routes.py
│   └── functional              # Функциональные тесты
       ├── test_auth.py
       ├── test_article.py
       └── test_comment.py
│   ├── static/                     # Статические файлы
│   │   ├── css/
│   │   │   └── styles.css         # Стили и темы оформления
│   │   └── js/
│   │       └── theme.js           # Переключение темы
│   │
│   ├── templates/                  # Шаблоны Jinja2
│   │   ├── articles/              # Шаблоны для статей
│   │   │   ├── form.html          # Форма создания/редактирования
│   │   │   ├── list.html          # Список статей
│   │   │   └── view.html          # Просмотр статьи
│   │   ├── auth/                  # Шаблоны авторизации
│   │   │   ├── login.html         # Форма входа
│   │   │   └── register.html      # Форма регистрации
│   │   ├── comments/              # Шаблоны комментариев
│   │   │   ├── _comment.html      # Шаблон комментария
│   │   │   └── _form.html         # Форма комментария
│   │   └── base.html              # Базовый шаблон
│   │
│   └── __init__.py                # Инициализация приложения
│├── instance 
│    ├──blog.db                     # База данных SQLite 
│
├── config.py                       # Конфигурация
├── requirements.txt                # Зависимости проекта
├── app.py                         # Точка входа
├── README.md                      # Документация
└── schema.sql                     # Схема базы данных
```

Install dependencies:
``` pip install -r requirements.txt```

For migration of the database, use the following command:
```flask migrations-cli migrate```
