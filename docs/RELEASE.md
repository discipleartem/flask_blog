# Release (dev → main)

Канон релиза flask_blog: PR `dev`/`release/*` **→** `main` (squash), GitHub Release с полным набором полей, sync `dev` ← `main`, архив ветки.

Справка API: [`github-releases-api.md`](github-releases-api.md).  
Skills: [`flask-blog-git-release`](../.cursor/skills/flask-blog-git-release/SKILL.md) · [`flask-blog-git-release-sync`](../.cursor/skills/flask-blog-git-release-sync/SKILL.md) · [`flask-blog-git-merged-archive`](../.cursor/skills/flask-blog-git-merged-archive/SKILL.md).

Триггеры агента: «релиз», «релиз в main», «release», «cut release» — Read и выполнить **`flask-blog-git-release`**.

После squash в `main` срабатывает auto-deploy ([`DEPLOY.md`](DEPLOY.md) §Auto-deploy).

---

## Поток

```text
  1. Подготовка на ветке release/vX.Y.Z (от актуального origin/dev)
       · bump version в pyproject.toml
       · docs/CHANGELOG.md: [Unreleased] → [X.Y.Z] — YYYY-MM-DD; пустой [Unreleased]
  2. PR release/vX.Y.Z → main  (только по запросу пользователя на PR)
  3. Squash merge в main
  4. GitHub Release (все поля заполнены — см. ниже)
  5. Sync: skill flask-blog-git-release-sync  (dev ← origin/main)
  6. Архив: release/vX.Y.Z → merged/vX.Y.Z  (flask-blog-git-merged-archive)
```

Шаги 8–10 global [`task-cycle.mdc`](~/.cursor/rules/task-cycle.mdc): PR integration→main → squash → sync. В этом репо sync после релиза — **project** skill `flask-blog-git-release-sync` (конфликты CHANGELOG/version → **main**).

---

## Обязательные поля GitHub Release

При «релиз» / «релиз в main» **запрещено** создавать Release с пустыми `name`/`body` или неявным target. Заполнить:

| Поле (API) | CLI `gh release create` | Значение в проекте |
|------------|-------------------------|--------------------|
| `tag_name` | позиционный `<tag>` | `vX.Y.Z` (= версия из `pyproject.toml` с префиксом `v`) |
| `name` | `--title` | `Flask Blog X.Y.Z` |
| `body` | `--notes-file` / `-F` | секция `[X.Y.Z]` из `docs/CHANGELOG.md` |
| `target_commitish` | `--target` | `main` |
| `draft` | флаг `--draft` или его отсутствие | явно published: **без** `--draft` |
| `prerelease` | `--prerelease` или нет | явно full: **без** `--prerelease` (иначе только по запросу) |
| `make_latest` | `--latest` | `--latest` для обычного релиза |
| `generate_release_notes` | `--generate-notes` | опционально; не вместо CHANGELOG |

Проверка: `gh release view "vX.Y.Z"` — непустые title и body, target/tag корректны.

---

## Версии и CHANGELOG

- SemVer в `pyproject.toml` `version = "X.Y.Z"`.
- Тег Release: `vX.Y.Z`.
- Перед PR в `main`: перенести пункты из `[Unreleased]` в `## [X.Y.Z] — YYYY-MM-DD`, оставить пустой `[Unreleased]`.
- Body Release = markdown этой секции (заголовок версии можно не дублировать в notes, если title уже задан).

---

## Чего не делать

- Push напрямую в `main` в обход PR (кроме явного запроса).
- Force-push `main` / `dev`.
- Release с target ≠ `main` без явного указания пользователя.
- Завершать релиз без sync `dev` ← `main`.
- Оставлять remote `release/*` без архива `merged/*` (см. [`git-merged-branches.mdc`](../.cursor/rules/git-merged-branches.mdc)).
