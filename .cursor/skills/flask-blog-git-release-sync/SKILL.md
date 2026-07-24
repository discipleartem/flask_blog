---
name: flask-blog-git-release-sync
description: >-
  After a release PR is merged into main (and GitHub Release with all fields):
  merge origin/main into dev, resolve release-file conflicts preferring main,
  push origin/dev. Use when user says sync after release, sync dev with main
  after vX.Y.Z, or post-release when git log dev..origin/main is not empty.
---

# flask_blog — sync `dev` ← `main` после релиза

Полный релиз (подготовка → PR → **GitHub Release со всеми полями** → этот sync): skill [`flask-blog-git-release`](../flask-blog-git-release/SKILL.md).  
Общий sync (не только релиз): skill [`git-dev-main-sync`](~/.cursor/skills/git-dev-main-sync/SKILL.md).  
Архив release-ветки: skill [`flask-blog-git-merged-archive`](../flask-blog-git-merged-archive/SKILL.md).  
API / поля Release: [`docs/github-releases-api.md`](../../../docs/github-releases-api.md) · процесс: [`docs/RELEASE.md`](../../../docs/RELEASE.md).

**Когда:** сразу после squash merge release-PR в `main` и создания GitHub Release (`gh release create` / API).  
**Цель:** `git log dev..origin/main --oneline` пуст; закончить на `dev`.

Если Release ещё не создан — сначала skill **`flask-blog-git-release`** §3 (все поля: tag, title, body, target=`main`, draft/prerelease явно, `--latest`), затем этот sync.

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
gh release view "${VERSION}"         # title/body непустые (если Release уже создан)
```

После успешного sync — архив `release/vX.Y.Z` → `merged/vX.Y.Z` (skill `flask-blog-git-merged-archive`).

## Нельзя

- Force-push `dev` / `main`
- Оставлять `[Unreleased]` с уже выпущенными пунктами (брать CHANGELOG с `main`)
- Завершать turn на `release/*` / `merged/*` вместо `dev`
- Bare `git pull origin main` без явной стратегии merge
- Считать релиз завершённым, если GitHub Release создан без title/body/target (исправить через `gh release edit` или skill `flask-blog-git-release`)
