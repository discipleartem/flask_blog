# Backlog

Список будущих задач проекта. Подход к реализации выбирается при взятии задачи в работу.
Выполненные задачи фиксируются в [`CHANGELOG.md`](CHANGELOG.md) и из этого файла удаляются.

Синхронизация с [GitHub Project «Flask Blog»](https://github.com/users/discipleartem/projects/6): `python ~/.cursor/skills/backlog-github-projects-sync/scripts/sync_backlog.py` (конфиг [`.github/backlog.json`](../.github/backlog.json)).

## Markdown-редактор для Post и Comment

**Статус:** in_review
**GitHub:** #44

### Проблема

Сейчас текст поста и комментария вводится как plain text без форматирования. Пользователям нужен web-редактор Markdown, чтобы размечать текст (заголовки, списки, ссылки, выделение и т.п.) при создании и редактировании Post и Comment.

### Acceptance criteria

- На формах создания/редактирования Post подключён Markdown-редактор EasyMDE (vendor в static, не CDN; JS обязателен для редактора).
- На формах создания/редактирования Comment — тот же подход.
- Канон в БД: `body_source` + `body_format`; для этих форм сервер всегда сохраняет `body_format=markdown` (клиентский format игнорируется).
- Витрина: HTML через серверный `render_to_html` + санитизация XSS (nh3); не сырой Markdown и не `| safe` по колонке из БД.
- Preview в тулбаре EasyMDE через `POST /markdown/preview` (тот же серверный рендер, что на витрине).
- Подсветка fenced-блоков на витрине/preview (`syntax-highlight.js`: python/html/js/css/bash + generic); автоотступы; кнопки копирования plain и Markdown с тостом.
- UI согласован с Bootstrap 5; без React/Vue и прочих SPA-фреймворков.
