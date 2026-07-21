---
name: flask-blog-docs-after-task
description: >-
  MUST run at end of flask_blog implementation: update ARCHITECTURE, DEVELOPMENT,
  CHANGELOG, AGENTS per mapping table, then commit. Triggers: end of
  implementation before done/push/PR; stop hook; user asks to update docs.
  Skip only for docs-only or no-behavior changes.
---

# flask_blog — документация после задачи

Канон: [`task-cycle.mdc`](~/.cursor/rules/task-cycle.mdc) ш.3 · pointer в [`00-project.mdc`](../../rules/00-project.mdc). Scoping: [`AGENTS.md`](../../../AGENTS.md), [`docs-context.mdc`](../../rules/docs-context.mdc).

Backlog/статусы — skill [`backlog-github-projects-sync`](~/.cursor/skills/backlog-github-projects-sync/SKILL.md) + [`backlog-status.mdc`](../../rules/backlog-status.mdc).  
Post-merge rename — skill [`flask-blog-git-merged-archive`](../flask-blog-git-merged-archive/SKILL.md).

## Когда выполнять

**Автоматически** в конце реализации — без запроса пользователя:

1. Перед финальным «готово» / push / PR — Read этот skill и выполнить ([`00-project.mdc`](../../rules/00-project.mdc)).
2. Hook `stop` ([`.cursor/hooks/docs-after-task-stop.py`](../../hooks/docs-after-task-stop.py)): если agent завершил turn на `feat|fix|chore` с app-изменениями без docs-sync — один auto follow-up.

После **завершения реализации** (все подзадачи), **перед** commit финализации / verify / push·PR.

## Когда пропустить

- Задача **только** `docs/` / `.cursor/rules/` / skills (без смены поведения приложения)
- Косметика / рефакторинг без смены API, схемы, маршрутов, UI-контракта
- Diff docs после шага 2 пустой — commit docs не нужен
- Hook не сработал и критериев «пропустить» нет — **всё равно** выполнить skill вручную

## Алгоритм

1. По `git diff` (working tree / staged; при необходимости `origin/dev...HEAD`) определить затронутые области.
2. Обновить **только** релевантные файлы из таблицы — факты, без дублей карт в rules.
3. Запись в [`docs/CHANGELOG.md`](../../../docs/CHANGELOG.md) `[Unreleased]` (Added / Changed / Fixed / Docs), если изменение заметно пользователю или агенту.
4. Если задача из [`docs/Backlog.md`](../../../docs/Backlog.md): при необходимости уточнить AC; **не** ставить `done` до merge в `dev`.
5. Commit: на task-ветке **auto** ([`git.mdc`](~/.cursor/rules/git.mdc) §Commits; Plan→Build→Agent).  
   - код + docs уместно → один `feat:`/`fix:` …  
   - только docs → `docs: …` (EN, Conventional Commits)  
   - пустой diff → commit пропустить
6. Дальше — verify / push / PR по project (не этот skill).

## Какой файл обновлять

| Изменения | Документ |
|-----------|----------|
| Маршруты, модули, права, поток запроса, карта `app/` | [`docs/ARCHITECTURE.md`](../../../docs/ARCHITECTURE.md) |
| Схема БД | `schema.sql` + `migrations/` + ARCHITECTURE §Данные |
| Howto: UI, Markdown/код-блоки, IronBee, локальный запуск | [`docs/DEVELOPMENT.md`](../../../docs/DEVELOPMENT.md) |
| Деплой / PA / CI hook | [`docs/DEPLOY.md`](../../../docs/DEPLOY.md) |
| Заметные фичи / фиксы | [`docs/CHANGELOG.md`](../../../docs/CHANGELOG.md) |
| Новый тип задачи для scoping | [`AGENTS.md`](../../../AGENTS.md) (+ при необходимости [`docs/README.md`](../../../docs/README.md)) |
| Запреты стека | [`.cursor/rules/00-project.mdc`](../../rules/00-project.mdc) (+ тематический `*.mdc`) |
| Алгоритм scoping | [`docs-context.mdc`](../../rules/docs-context.mdc) |

Не копировать таблицы ARCHITECTURE в rules. Индекс docs: [`docs/README.md`](../../../docs/README.md).

## Принципы

- Минимальный diff: только изменившиеся факты
- Не копировать код в docs — ссылка на модуль/маршрут достаточна
- Не фиксировать точные числа тестов/LOC в docs
- Витрина Markdown / подсветка / копирование — DEVELOPMENT §Контент, не дублировать в ARCHITECTURE

## После merge в `dev` (не этот skill целиком)

1. Backlog: `done` → sync → CHANGELOG (если ещё нет) → **удалить** секцию из `Backlog.md` — skill backlog-sync.
2. Ветки: `feat|docs/…` → `merged/…`, **checkout `dev`** — skill `flask-blog-git-merged-archive`.
