---
trigger: always_on
---
# 🧠 Правила разработки для Flask 3+

## 1. Общие принципы

* Используй Python ≥ 3.9 (Flask 3+ не поддерживает устаревшие версии Python). ([flask.palletsprojects.com][1])
* Следуй принципам:

  * DRY (не дублируй код)
  * KISS (простота)
  * YAGNI (не реализуй лишнего)
* Flask — минималистичный фреймворк, не перегружай архитектуру без необходимости.

---

## 2. Архитектура приложения

* Используй **Application Factory Pattern**:

  ```python
  def create_app(config=None):
      app = Flask(__name__)
      if config:
          app.config.from_object(config)
      return app
  ```

* Разделяй приложение на:

  * Blueprints (модули)
  * services (бизнес-логика)
  * models (данные)
  * routes (контроллеры)

* Не размещай бизнес-логику во view-функциях.

---

## 3. Работа с Blueprint

* Всегда используй Blueprint для масштабируемости:

  ```python
  bp = Blueprint("users", __name__, url_prefix="/users")
  ```
* Регистрируй Blueprint в factory:

  ```python
  app.register_blueprint(users_bp)
  ```

---

## 4. Конфигурация

* Используй config-объекты или env:

  * `.env`, `.flaskenv`
* Не используй устаревшие переменные:

  * ❌ FLASK_ENV (удалён в Flask 2.3+) ([flask.palletsprojects.com][1])

---

## 5. Контексты (ВАЖНО)

* Используй `g` для хранения данных запроса:

  ```python
  from flask import g
  g.user = current_user
  ```
* Не используй устаревшие `_app_ctx_stack` или `_request_ctx_stack`. ([flask.palletsprojects.com][1])

---

## 6. JSON и сериализация

* Используй `app.json` вместо старых encoder/decoder:

  ```python
  app.json.ensure_ascii = False
  ```
* Не переопределяй `json_encoder` (устарело). ([flask.palletsprojects.com][1])

---

## 7. Асинхронность

* Flask 3 поддерживает async view:

  ```python
  @app.get("/data")
  async def get_data():
      return {"status": "ok"}
  ```
* Используй async только при реальной необходимости.

---

## 8. Обработка ошибок

* Используй централизованные обработчики:

  ```python
  @app.errorhandler(404)
  def not_found(e):
      return {"error": "Not found"}, 404
  ```

---

## 9. Безопасность

* Всегда задавай:

  * SECRET_KEY
* Используй:

  * TRUSTED_HOSTS
  * ограничения размеров запросов (MAX_CONTENT_LENGTH) ([flask.palletsprojects.com][1])
* Не доверяй входящим данным.

---

## 10. Работа с запросами

* Используй:

  ```python
  request.get_json()
  ```
* Не используй устаревшее:

  * `request.json`

---

## 11. CLI и запуск

* Используй CLI:

  ```bash
  flask --app app run
  ```
* Не запускай через `app.run()` в production.

---

## 12. Тестирование

* Используй test_client:

  ```python
  with app.test_client() as client:
      response = client.get("/")
  ```

---

## 13. Работа с зависимостями

* Учитывай:

  * Werkzeug ≥ 3.x обязателен ([flask.palletsprojects.com][1])
* Следи за совместимостью расширений (многие ломаются при Flask 3)

---

## 14. Что запрещено

* ❌ Использовать deprecated API
* ❌ Хранить состояние вне контекста запроса
* ❌ Писать монолитные app.py на 1000+ строк
* ❌ Логика в шаблонах Jinja

---

## 15. Рекомендации по структуре проекта

```
project/
│
├── app/
│   ├── __init__.py
│   ├── routes/
│   ├── services/
│   ├── models/
│   └── extensions.py
│
├── config.py
├── wsgi.py
└── run.py
```

---

## 16. Современные особенности Flask 3+

* Удалены устаревшие API
* Улучшена типизация
* Контексты работают через contextvars (лучше производительность) ([flask.palletsprojects.com][1])
* Добавлена поддержка async iterable response
* Улучшена безопасность cookies (Partitioned cookies)

---

## 17. Когда использовать расширения

Используй только если нужно:

* Flask-SQLAlchemy → если есть БД
* Flask-Migrate → если есть миграции
* Flask-Login → если есть авторизация

Не добавляй "на всякий случай".

---

# 📌 Итог

Пиши Flask-приложения:

* модульно
* минималистично
* без устаревших API
* с учётом async и новых механизмов Flask 3+

[1]: https://flask.palletsprojects.com/en/stable/changes/?utm_source=chatgpt.com "Changes — Flask Documentation (3.1.x)"
