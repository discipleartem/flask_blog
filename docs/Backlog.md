# Backlog

Список будущих задач проекта. Подход к реализации выбирается при взятии задачи в работу.
Выполненные задачи фиксируются в [`CHANGELOG.md`](CHANGELOG.md) и из этого файла удаляются.

Синхронизация с [GitHub Project «Flask Blog»](https://github.com/users/discipleartem/projects/6): `python ~/.cursor/skills/backlog-github-projects-sync/scripts/sync_backlog.py` (конфиг [`.github/backlog.json`](../.github/backlog.json)).

## Обновление документации

**Статус:** in_review
**GitHub:** #47

### Проблема

При постановке и выполнении задач агент сканирует весь репозиторий: нет дешёвого роутера (AGENTS), индекса docs и плотной архитектурной карты. Дубли между DEVELOPMENT и rules раздувают контекст. Нужна docs-first документация, чтобы сужать чтение до 1–3 файлов docs и точечных путей в коде и снизить расход токенов.

### Acceptance criteria

- Есть `AGENTS.md`: таблица тип задачи → docs → пути кода → что не читать.
- Есть `docs/README.md` (индекс) и `docs/ARCHITECTURE.md` (маршруты, схема, карта `app/`, права) — плотные таблицы, без howto.
- `DEVELOPMENT.md` не дублирует структуру/права: ссылки на ARCHITECTURE.
- Короткое alwaysApply-правило `docs-context.mdc` + ссылка в `00-project.mdc`.
- Project skill `flask-blog-docs-after-task`: автозапуск в конце реализации (`flask-blog-workflow.mdc` + hook `stop`); таблица куда писать + CHANGELOG; связан с `docs-context` / AGENTS / backlog-sync.
- README §Документация указывает AGENTS / индекс / ARCHITECTURE.
- CHANGELOG (Unreleased / Docs) отражает обновление.
- Sync backlog ↔ GitHub Project выполнен (`**GitHub:** #N` в секции).
