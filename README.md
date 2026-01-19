# Flask Blog

Веб-приложение блога на Flask — многопользовательская платформа с возможностью публикации постов и обсуждений.

## Технологический стек

* **Backend:** Python 3.13, Flask 3.0.3
* **Database:** SQLite (чистый SQL без ORM)
* **Frontend:** Bootstrap 5 (Jinja2 templates)
* **Инструменты:** Pytest (для тестирования)

## Требования

* Python 3.13 или выше

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone <repository-url>
   cd flask_blog
   ```

2. Создайте виртуальное окружение и активируйте его:
   ```bash
   python -m venv .venv
   # Для Linux/macOS:
   source .venv/bin/activate
   # Для Windows:
   .venv\Scripts\activate
   ```

3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

   Для разработки (включая pytest):
   ```bash
   pip install -e ".[dev]"
   ```

## Инициализация базы данных

Перед первым запуском необходимо создать таблицы в базе данных:

```bash
flask --app app init-db
```