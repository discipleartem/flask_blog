---
name: flask-blog-git-release
description: >-
  Cut a flask_blog release to main: prepare CHANGELOG/version, PR squash into
  main, create GitHub Release with ALL fields filled (tag, title, body, target,
  draft/prerelease, latest), then sync dev and archive release/*. Use when user
  says релиз, релиз в main, release, or cut release.
---

# flask_blog — релиз в `main`

Канон: [`docs/RELEASE.md`](../../../docs/RELEASE.md) · API: [`docs/github-releases-api.md`](../../../docs/github-releases-api.md).

После merge: sync — [`flask-blog-git-release-sync`](../flask-blog-git-release-sync/SKILL.md); архив — [`flask-blog-git-merged-archive`](../flask-blog-git-merged-archive/SKILL.md).  
PR/commit процедуры: [`git-commit-pr`](~/.cursor/skills/git-commit-pr/SKILL.md).

**Триггеры:** «релиз», «релиз в main», «release», «cut release».

## Жёсткое правило: все поля Release

При `gh release create` / `POST …/releases` **обязательно** задать (не оставлять пустыми и не полагаться на молчаливые defaults для смысла релиза):

| Поле | Обязательно | Значение по умолчанию в проекте |
|------|-------------|----------------------------------|
| `tag_name` / tag | да | `vX.Y.Z` |
| `name` / `--title` | да | `Flask Blog X.Y.Z` |
| `body` / `-F` notes | да | секция `[X.Y.Z]` из `docs/CHANGELOG.md` |
| `target_commitish` / `--target` | да | `main` |
| `draft` | явно | published → **не** передавать `--draft` |
| `prerelease` | явно | full → **не** передавать `--prerelease` (иначе только если пользователь просил pre) |
| `make_latest` / `--latest` | да | `--latest` для обычного релиза |
| `generate_release_notes` | решить явно | предпочтение: body из CHANGELOG; `--generate-notes` только как дополнение |

**Запрещено:** `gh release create vX.Y.Z` без `--title`, без notes, без `--target`.

---

## Алгоритм

### 0. Версия и предпосылки

```bash
git fetch origin
# origin/dev актуален; git log origin/dev..origin/main — пуст (иначе сначала sync)
VERSION=0.4.0          # SemVer без v — согласовать с пользователем / Unreleased
TAG="v${VERSION}"
TITLE="Flask Blog ${VERSION}"
```

### 1. Ветка подготовки

```bash
git checkout dev && git pull --ff-only origin dev
git checkout -b "release/${TAG}"
```

- `pyproject.toml`: `version = "${VERSION}"`
- `docs/CHANGELOG.md`: перенести `[Unreleased]` → `## [${VERSION}] — YYYY-MM-DD`; оставить пустой `[Unreleased]`
- Commit: `chore: release ${TAG}`
- Push: `git push -u origin HEAD`

### 2. PR → `main` (только по запросу на PR)

```bash
gh pr create --base main --head "release/${TAG}" --title "Release ${TAG}" --body "…"
# после approve / по запросу:
gh pr merge --squash --delete-branch=false
git fetch origin
```

Дождаться, что `origin/main` содержит squash (CI/deploy могут идти параллельно — см. DEPLOY).

### 3. GitHub Release — полный набор полей

Извлечь body из CHANGELOG (секция версии) во временный файл, затем:

```bash
# /tmp/release-body.md — markdown секции [X.Y.Z] (без пустого Unreleased)

gh release create "${TAG}" \
  --title "${TITLE}" \
  --notes-file /tmp/release-body.md \
  --target main \
  --latest
```

Эквивалент REST (`gh api`):

```bash
gh api repos/{owner}/{repo}/releases \
  -f tag_name="${TAG}" \
  -f target_commitish=main \
  -f name="${TITLE}" \
  -f body="$(cat /tmp/release-body.md)" \
  -F draft=false \
  -F prerelease=false \
  -F generate_release_notes=false \
  -f make_latest=true
```

Проверка:

```bash
gh release view "${TAG}"
# title и body непустые; tag = TAG
```

Опционально (дополнение к CHANGELOG, не замена):

```bash
gh release create "${TAG}" \
  --title "${TITLE}" \
  --notes-file /tmp/release-body.md \
  --generate-notes \
  --target main \
  --latest
```

### 4. Sync `dev` ← `main`

Выполнить skill **`flask-blog-git-release-sync`** с `VERSION=${TAG}`.

### 5. Архив ветки

Skill **`flask-blog-git-merged-archive`**: `release/vX.Y.Z` → `merged/vX.Y.Z`, закончить на `dev`.

---

## Нельзя

- Release без title/body/target
- `target` ≠ `main` без явного указания пользователя
- Force-push `main` / `dev`
- Завершать turn без sync после merge в `main`
- Создавать PR в `main` без запроса пользователя на PR (подготовка ветки/CHANGELOG — можно)
