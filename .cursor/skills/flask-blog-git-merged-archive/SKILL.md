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

## Follow-up (backlog `done` / docs)

Если нужен отдельный PR (`docs/…-backlog-done`):

1. Ветка **от актуального `dev`**, коммит, push, `gh pr create --base dev`
2. Сразу после push/PR: `git checkout dev`
3. После merge docs-PR — снова полный алгоритм выше

## Запрещено

- Удалять remote task без `origin/merged/…`
- PR / работа с head `merged/…`
- Force-push `main` / `dev`
- Завершать turn на task / `docs/*` / `merged/*` вместо `dev` (или `main`)
