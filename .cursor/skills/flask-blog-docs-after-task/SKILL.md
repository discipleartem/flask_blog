---
name: flask-blog-docs-after-task
description: >-
  MUST run at end of flask_blog implementation AND before any PR to dev:
  update ARCHITECTURE, DEVELOPMENT, CHANGELOG, AGENTS per mapping table,
  backlog in_review + sync, then commit. Triggers: end of implementation;
  before push/PR to integration; stop hook; user asks to update docs.
  Skip only for docs-only or no-behavior changes.
---

# flask_blog — документация после задачи

Канон: [`task-cycle.mdc`](~/.cursor/rules/task-cycle.mdc) · pointer в [`00-project.mdc`](../../rules/00-project.mdc). Scoping: [`AGENTS.md`](../../../AGENTS.md), [`docs-context.mdc`](../../rules/docs-context.mdc).

Backlog/статусы — skill [`backlog-github-projects-sync`](~/.cursor/skills/backlog-github-projects-sync/SKILL.md) + [`backlog-status.mdc`](../../rules/backlog-status.mdc).  
Post-merge rename — skill [`flask-blog-git-merged-archive`](../flask-blog-git-merged-archive/SKILL.md).

## Gate (жёстко)

**Запрещено** `gh pr create` / открывать PR task → `dev`, пока этот skill не выполнен в текущей ветке (docs актуальны относительно `origin/dev...HEAD`, коммит сделан при необходимости, backlog `in_review` + sync если задача из Backlog).

Порядок финала: **docs-after-task → verify → push → PR**. Не наоборот.

## Когда выполнять

**Автоматически** — без запроса пользователя:

1. В конце реализации (все подзадачи закрыты).
2. **Снова / обязательно**, если пользователь просит PR в `dev`, а skill ещё не гоняли после последних app-изменений.
3. Hook `stop` ([`.cursor/hooks/docs-after-task-stop.py`](../../hooks/docs-after-task-stop.py)): `feat|fix|chore` с app-изменениями без docs-sync — один auto follow-up.

Перед «готово» / push / PR — **Read этот skill целиком** и выполнить.

## Когда пропустить

- Задача **только** `docs/` / `.cursor/rules/` / skills (без смены поведения приложения) — кроме случая, когда правка и есть «docs-after-task»
- Косметика / рефакторинг без смены API, схемы, маршрутов, UI-контракта
- Diff docs после шага 2 пустой — commit docs не нужен (skill всё равно **прогнать**: проверить mapping + backlog статус перед PR)
- Критериев skip нет, а hook не сработал — **всё равно** выполнить вручную

## Алгоритм

1. По `git diff` (working tree / staged; **обязательно** `origin/dev...HEAD` перед PR) определить затронутые области.
2. Обновить **только** релевантные файлы из таблицы — факты, без дублей карт в rules.
3. Запись в [`docs/CHANGELOG.md`](../../../docs/CHANGELOG.md) `[Unreleased]` (Added / Changed / Fixed / Docs), если изменение заметно пользователю или агенту.
4. Если задача из [`docs/Backlog.md`](../../../docs/Backlog.md):
   - уточнить AC при необходимости;
   - **перед PR в `dev`:** статус → `in_review`, затем `python ~/.cursor/skills/backlog-github-projects-sync/scripts/sync_backlog.py`;
   - **не** ставить `done` до merge в `dev`.
5. Commit на task-ветке (**auto**, [`git.mdc`](~/.cursor/rules/git.mdc) §Commits):
   - код + docs уместно → один `feat:`/`fix:` …  
   - только docs → `docs: …` (EN, Conventional Commits)  
   - пустой diff → commit пропустить
6. Дальше (вне этого skill): verify → `git push` → PR через skill [`git-commit-pr`](~/.cursor/skills/git-commit-pr/SKILL.md) **только после** шагов 1–5.

## Какой файл обновлять

| Изменения | Документ |
|-----------|----------|
| Маршруты, модули, права, поток запроса, карта `app/` | [`docs/ARCHITECTURE.md`](../../../docs/ARCHITECTURE.md) |
| Схема БД | `schema.sql` + `migrations/` + ARCHITECTURE §Данные |
| Howto: UI, Markdown/код-блоки, IronBee, локальный запуск | [`docs/DEVELOPMENT.md`](../../../docs/DEVELOPMENT.md) |
| Деплой / PA / CI hook | [`docs/DEPLOY.md`](../../../docs/DEPLOY.md) |
| Релиз / GitHub Release / sync skills | [`docs/RELEASE.md`](../../../docs/RELEASE.md), [`docs/github-releases-api.md`](../../../docs/github-releases-api.md) |
| Заметные фичи / фиксы | [`docs/CHANGELOG.md`](../../../docs/CHANGELOG.md) |
| Новый тип задачи для scoping | [`AGENTS.md`](../../../AGENTS.md) (+ при необходимости [`docs/README.md`](../../../docs/README.md)) |
| Запреты стека / gate docs→PR | [`.cursor/rules/00-project.mdc`](../../rules/00-project.mdc) (+ тематический `*.mdc`) |
| Алгоритм scoping | [`docs-context.mdc`](../../rules/docs-context.mdc) |

Не копировать таблицы ARCHITECTURE в rules. Индекс docs: [`docs/README.md`](../../../docs/README.md).

## Принципы

- Минимальный diff: только изменившиеся факты
- Не копировать код в docs — ссылка на модуль/маршрут достаточна
- Не фиксировать точные числа тестов/LOC в docs
- Витрина Markdown / подсветка / копирование — DEVELOPMENT §Контент, не дублировать в ARCHITECTURE

## После merge в `dev` (не этот skill целиком)

1. Backlog: `done` → sync → CHANGELOG (если ещё нет) → **удалить** секцию из `Backlog.md` — skill backlog-sync + skill [`flask-blog-git-merged-archive`](../flask-blog-git-merged-archive/SKILL.md) (docs-PR **сразу** squash-merge в том же turn; не ждать пользователя).
2. Ветки: `feat|docs/…` → `merged/…`, **checkout `dev`** — тот же skill `flask-blog-git-merged-archive`.
