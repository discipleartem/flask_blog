---
name: flask-blog-git-release-sync
description: >-
  After a release PR is merged into main (and optional GitHub Release): merge
  origin/main into dev, resolve release-file conflicts preferring main, push
  origin/dev. Use when user says sync after release, sync dev with main after
  vX.Y.Z, or post-release when git log dev..origin/main is not empty.
---

# flask_blog — sync `dev` ← `main` после релиза

Общий sync (не только релиз): skill [`git-dev-main-sync`](~/.cursor/skills/git-dev-main-sync/SKILL.md).  
Архив release-ветки: skill [`flask-blog-git-merged-archive`](../flask-blog-git-merged-archive/SKILL.md).

**Когда:** сразу после squash merge release-PR в `main` (и при необходимости `gh release create`).  
**Цель:** `git log dev..origin/main --oneline` пуст; закончить на `dev`.

## Алгоритм

```bash
git fetch origin
VERSION=v0.3.0   # тег / версия только что выпущенного релиза

git checkout dev
git pull --ff-only origin dev

git merge origin/main -m "chore: sync dev with main after ${VERSION}"
```

### Конфликты (типично после squash release)

История `dev`/`main` расходится — **content** конфликты на файлах релиза:

| Файл | Резолюция |
|------|-----------|
| `docs/CHANGELOG.md` | **main** (`--theirs` при merge на `dev`) — секция `[0.x.y]`, пустой `[Unreleased]` |
| `pyproject.toml` (`version`) | **main** |
| `README.md` (badge / возможности релиза) | **main**, если конфликт про версию/релизные bullets |

```bash
# пример: только CHANGELOG
git checkout --theirs docs/CHANGELOG.md
git add docs/CHANGELOG.md
# остальные конфликты — по таблице; затем:
git commit --no-edit   # или -m "chore: sync dev with main after ${VERSION}"
```

`--theirs` = `origin/main` **только** когда текущая ветка — `dev` и идёт `merge origin/main`.

### Push и проверка

```bash
git push origin dev
git log dev..origin/main --oneline   # must be empty
git status -sb                       # на dev
```

После успешного sync — при необходимости архив `release/vX.Y.Z` → `merged/vX.Y.Z` (skill `flask-blog-git-merged-archive`).

## Нельзя

- Force-push `dev` / `main`
- Оставлять `[Unreleased]` с уже выпущенными пунктами (брать CHANGELOG с `main`)
- Завершать turn на `release/*` / `merged/*` вместо `dev`
- Bare `git pull origin main` без явной стратегии merge
