# Backlog

Список будущих задач проекта. Подход к реализации выбирается при взятии задачи в работу.
Выполненные задачи фиксируются в [`CHANGELOG.md`](CHANGELOG.md) и из этого файла удаляются.

Синхронизация с [GitHub Project «Flask Blog»](https://github.com/users/discipleartem/projects/6): `python ~/.cursor/skills/backlog-github-projects-sync/scripts/sync_backlog.py` (конфиг [`.github/backlog.json`](../.github/backlog.json)).

## Обновление дизайна сайта

**Статус:** in_review
**GitHub:** #51

### Проблема

Текущий UI выглядит устаревшим / шаблонным. Нужно обновить визуальный дизайн сайта, опираясь **только на Bootstrap 5** (серверные Jinja-шаблоны + CSS проекта). Без front-end фреймворков (React, Vue и т.п.), без смены стека UI.

### Acceptance criteria

- Дизайн обновлён с использованием компонентов и утилит Bootstrap 5; кастомный CSS минимален и не дублирует то, что даёт Bootstrap.
- Обновлены ключевые поверхности: layout/навигация, лента постов, страница поста, формы (login / комментарии / редактирование), админские экраны пользователей (если затронуты общим layout).
- Сохранена текущая структура маршрутов и разметки логики (auth, CSRF, права) — меняется только представление.
- Тема и типографика согласованы между страницами; адаптив (mobile / desktop) работает.
- Нет подключения React/Vue/Angular/Svelte и аналогов; UI остаётся Jinja2 + Bootstrap 5.
- CHANGELOG (Unreleased / Changed или Docs) отражает обновление дизайна.
- Sync backlog ↔ GitHub Project выполнен (`**GitHub:** #N` в секции).
