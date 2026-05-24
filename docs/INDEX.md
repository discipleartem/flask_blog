# 📚 Flask Blog — Документация

**Версия:** 0.1.0 | **Дата:** Май 2026
**Python:** 3.12 (default) | **Flask:** ≥ 3.0.0
**БД:** SQLite (чистый SQL) | **Лицензия:** MIT

---

## Навигация по документации

| Документ | Содержание |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Обзор, архитектура (Clean Architecture), структура проекта, паттерны и принципы |
| [LAYERS.md](LAYERS.md) | Детальный разбор всех слоёв: фабрика, конфигурация, БД, модели, репозитории, сервисы, представления, аутентификация, CLI |
| [DATABASE.md](DATABASE.md) | Схема БД, системные роли, система миграций |
| [SECURITY.md](SECURITY.md) | JWT-авторизация, брутфорс-защита, CSRF, XSS, cookies |
| [FRONTEND.md](FRONTEND.md) | Шаблоны Jinja2, статические файлы (CSS/JS), темизация |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Установка, запуск, тестирование, Make-команды, план развития |

## Быстрые ссылки

- [README.md](../README.md) — краткая инструкция
- [flask-blog-plan.md](flask-blog-plan.md) — полный план развития
- [database-migrations-tz.md](database-migrations-tz.md) — ТЗ миграций
- [jwt-service-tz.md](jwt-service-tz.md) — ТЗ JWT-сервиса
- [flask-3.0-documentation.md](flask-3.0-documentation.md) — документация Flask 3.0

---

## Ключевые возможности

| Возможность | Описание |
|---|---|
| 🔐 Аутентификация | Самописная JWT-авторизация (HS256) через cookies |
| 👤 Дискриминаторы | Несколько аккаунтов с одинаковым логином (login#1234) |
| 🛡️ Роли | Admin, Moderator, User |
| 🚫 Брутфорс-защита | Flask-Limiter + LoginAttemptService |
| 🌓 Темизация | Тёмная/светлая тема |
| 📝 CRUD блога | Посты и комментарии |
| 🗄️ Чистый SQL | Без ORM |
| 📦 Миграции | Ручные SQL-миграции с версионированием |

---

*Документация создана на основе анализа исходного кода, май 2026.*