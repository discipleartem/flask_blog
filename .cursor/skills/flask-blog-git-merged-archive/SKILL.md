---
name: flask-blog-git-merged-archive
description: >-
  After PR MERGED / post-merge: rename task branch to merged/<short> locally and
  on origin, delete old remote name, checkout integration (dev). Also follow-up
  docs/backlog PR then return to dev. Use when user says merged, MERGED, or
  archive branch as merged/*.
---

# flask_blog — archive task branch as `merged/*`

Policy: [`.cursor/rules/git-merged-branches.mdc`](../../rules/git-merged-branches.mdc). Global default local-only — **этот репо** требует remote archive.

Выполнять **в одном turn** после merge / `MERGED`.

```bash
git fetch origin
INTEGRATION=dev   # или main, если merge был в main
TASK=feat/my-task # head PR до merge
SHORT=my-task     # без префикса feat|/docs|/fix|/chore|

# 1) Сначала на integration
git checkout "$INTEGRATION"
git pull --ff-only origin "$INTEGRATION"

# 2) Локальный rename (+ remote archive)
if git show-ref --verify --quiet "refs/heads/$TASK"; then
  git branch -m "$TASK" "merged/$SHORT"
else
  git branch "merged/$SHORT" "origin/$TASK"
fi
git push -u origin "merged/$SHORT"
git push origin --delete "$TASK"

# 3) Снова integration
git checkout "$INTEGRATION"
git status -sb
```

## Follow-up

**Release → `main`:** полный поток — skill [`flask-blog-git-release`](../flask-blog-git-release/SKILL.md); после merge — sync [`flask-blog-git-release-sync`](../flask-blog-git-release-sync/SKILL.md), затем архив `release/…` этим skill.

### Backlog `done` / очистка `Backlog.md` (тот же turn)

Если смерженный PR закрывал задачу из [`docs/Backlog.md`](../../../docs/Backlog.md) — **не оставлять** открытый docs-PR и **не** заканчивать turn, пока секция задачи ещё есть на `origin/dev`.

Иначе: пользователь видит «живую» задачу после merge фичи; параллельные правки `Backlog.md` → merge-конфликты.

Алгоритм (после шага архива task-ветки, на актуальном `dev`):

```bash
git checkout -b docs/<short>-backlog-done   # от origin/dev
# 1) **Статус:** done → sync_backlog.py
# 2) CHANGELOG [Unreleased]/Docs: задача #N выполнена…
# 3) Удалить ##-секцию задачи из Backlog.md
git add docs/Backlog.md docs/CHANGELOG.md
git commit -m "docs: mark backlog #N done after merge"
git push -u origin HEAD
gh pr create --base dev --title "docs: mark backlog #N done" --body "…"
gh pr merge --squash          # СРАЗУ в этом turn — не ждать пользователя
git fetch origin
# архив docs-ветки тем же алгоритмом → merged/<short>-backlog-done
git checkout dev && git pull --ff-only origin dev
# проверка: секции задачи нет в docs/Backlog.md
```

Кратко: **create → merge → archive docs → на `dev`**. Открытый `docs/*-backlog-done` без merge — ошибка процесса.

## Запрещено

- Удалять remote task без `origin/merged/…`
- PR / работа с head `merged/…`
- Force-push `main` / `dev`
- Завершать turn на task / `docs/*` / `merged/*` вместо `dev` (или `main`)
- Завершать MERGED-turn с открытым PR `docs/*-backlog-done` или с секцией закрытой задачи всё ещё в `origin/dev:docs/Backlog.md`
