# GitHub Projects API (Projects v2)

Справка по возможностям и API для синхронизации [`Backlog.md`](Backlog.md) с доской [Flask Blog](https://github.com/users/discipleartem/projects/6).  
Канон sync: skill `backlog-github-projects-sync` · конфиг [`.github/backlog.json`](../.github/backlog.json).

Официально:

- [Using the API to manage Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-api-to-manage-projects)
- [GraphQL reference: Projects](https://docs.github.com/en/graphql/reference/projects)
- [REST: Projects](https://docs.github.com/en/rest/projects/projects) · [REST: Project items](https://docs.github.com/en/rest/projects/items)
- Classic: [sunset](https://github.blog/changelog/2024-05-23-sunset-notice-projects-classic/) (REST classic снят; не использовать)

---

## 1. Возможности Projects v2

| Возможность | Суть |
|-------------|------|
| **Items** | Issue, Pull Request или **draft issue** (карточка только на доске) |
| **Fields** | Встроенные (Title, Assignees, Labels, Milestone, Repository, Linked PRs, Parent issue, Sub-issues progress, даты) + **custom** (single select, text, number, date, iteration) |
| **Status** | Обычно single select (колонки board): у Flask Blog — `Backlog`, `In progress`, `In review`, `Done` |
| **Priority** | Custom single select; у Flask Blog — **`P0` / `P1` / `P2`** (не Urgent/High/Medium/Low) |
| **Size / Estimate / dates** | У Flask Blog есть `Size` (XS…XL), `Estimate`, `Start date`, `Target date` |
| **Views** | Table / Board / Roadmap; фильтры, группировка, сортировка (через UI; API views ограничен) |
| **Draft issues** | Быстрые карточки без issue в репо; можно конвертировать в Issue |
| **Linked issues / sub-issues** | Issue ↔ project item; parent/sub-issues на уровне Issues |
| **Workflows / automations** | Встроенные правила доски + Actions |
| **Insights** | Графики в UI |

**Projects (classic)** — deprecated/sunset; для новой автоматизации только **Projects v2** (`ProjectV2`).

---

## 2. Auth и scopes

| Способ | Scope / permission |
|--------|-------------------|
| PAT (classic) / `gh` token | Чтение: `read:project`; запись: **`project`** |
| Fine-grained PAT | Permission **Projects** (Read or Read and write) на owner проекта |
| GitHub App | Permission **Projects** (+ Contents и др. при `createProjectV2` с `repositoryId`) |

Проверка CLI:

```bash
gh auth status          # в scopes должен быть project
gh auth refresh -s project
```

Endpoint GraphQL: `POST https://api.github.com/graphql`  
Заголовок: `Authorization: Bearer <TOKEN>`.

---

## 3. GraphQL vs REST vs `gh`

| Канал | Когда |
|-------|--------|
| **GraphQL ProjectsV2** | Полный CRUD полей/items; канон для автоматизации |
| **REST `…/projectsV2`** | Список/get проектов и items (удобно для простых клиентов) |
| **`gh project …`** | Обёртка над GraphQL; то, чем пользуется sync-скрипт |

CLI (`gh project`): `list`, `view`, `create`, `edit`, `close`, `delete`, `copy`, `field-list` / `field-create` / `field-delete`, `item-list` / `item-add` / `item-create` (draft) / `item-edit` / `item-archive` / `item-delete`, `link` / `unlink`, `mark-template`.

---

## 4. Ключевые GraphQL queries

### Node ID user-проекта

```graphql
query {
  user(login: "discipleartem") {
    projectV2(number: 6) {
      id
      title
    }
  }
}
```

Flask Blog: `id` ≈ `PVT_kwHOAG7bZs4BdzUF`, number `6`.

### Поля (в т.ч. option id для Status / Priority)

```graphql
query {
  node(id: "PROJECT_ID") {
    ... on ProjectV2 {
      fields(first: 30) {
        nodes {
          ... on ProjectV2Field { id name }
          ... on ProjectV2SingleSelectField {
            id name
            options { id name }
          }
          ... on ProjectV2IterationField {
            id name
            configuration { iterations { id startDate } }
          }
        }
      }
    }
  }
}
```

Эквивалент CLI: `gh project field-list 6 --owner discipleartem --format json`.

### Items + значения полей

```graphql
query {
  node(id: "PROJECT_ID") {
    ... on ProjectV2 {
      items(first: 20) {
        nodes {
          id
          content {
            ... on Issue { number title }
            ... on PullRequest { number title }
            ... on DraftIssue { title body }
          }
          fieldValues(first: 15) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue {
                name
                field { ... on ProjectV2FieldCommon { name } }
              }
              ... on ProjectV2ItemFieldTextValue {
                text
                field { ... on ProjectV2FieldCommon { name } }
              }
            }
          }
        }
      }
    }
  }
}
```

---

## 5. Ключевые GraphQL mutations

> Нельзя в одном вызове и добавить item, и выставить поле: сначала `addProjectV2ItemById`, затем `updateProjectV2ItemFieldValue`.

| Mutation | Назначение |
|----------|------------|
| `createProjectV2` | Создать проект |
| `updateProjectV2` | Настройки (title, public, readme, …) |
| `deleteProjectV2` | Удалить проект |
| `addProjectV2ItemById` | Добавить Issue/PR по `contentId` |
| `addProjectV2DraftIssue` | Draft-карточка |
| `updateProjectV2ItemFieldValue` | Status, Priority, text/number/date/iteration |
| `clearProjectV2ItemFieldValue` | Сбросить поле |
| `deleteProjectV2Item` | Убрать item с доски |
| `archiveProjectV2Item` | Архив |
| `convertProjectV2DraftIssueItemToIssue` | Draft → Issue |
| `createProjectV2Field` / `deleteProjectV2Field` | Custom fields |
| `linkProjectV2ToRepository` / `unlink…` | Связь с репо |

### Добавить Issue/PR

```graphql
mutation {
  addProjectV2ItemById(input: {
    projectId: "PROJECT_ID"
    contentId: "ISSUE_OR_PR_NODE_ID"
  }) {
    item { id }
  }
}
```

CLI: `gh project item-add 6 --owner discipleartem --url https://github.com/OWNER/REPO/issues/N`.

### Выставить single select (Status / Priority)

```graphql
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "PROJECT_ID"
    itemId: "ITEM_ID"
    fieldId: "FIELD_ID"
    value: { singleSelectOptionId: "OPTION_ID" }
  }) {
    projectV2Item { id }
  }
}
```

CLI: `gh project item-edit --id ITEM_ID --project-id PROJECT_ID --field-id FIELD_ID --single-select-option-id OPTION_ID`.

### Assignees / Labels / Milestone

Это поля **issue/PR**, не project item. Менять через Mutations Issues (`addAssigneesToAssignable`, `addLabelsToLabelable`, …), не через `updateProjectV2ItemFieldValue`.

---

## 6. REST (Projects v2)

Примеры (user-owned):

| Метод | Path |
|-------|------|
| GET | `/users/{username}/projectsV2` |
| GET | `/users/{username}/projectsV2/{project_number}` |
| GET | `/orgs/{org}/projectsV2` · `/orgs/{org}/projectsV2/{project_number}` |
| GET/POST/… | `/users/{username}/projectsV2/{project_number}/items` (и org-аналоги) |

Заголовки: `Accept: application/vnd.github+json`, `Authorization: Bearer …`.

Для полного управления custom fields GraphQL обычно удобнее REST.

---

## 7. Маппинг на backlog flask_blog

Локальный канон — `docs/Backlog.md`. На GitHub: **Issue** (тело) + **Project item** (колонка Status, Priority).

### Status → `**Статус:**`

| Ключ в Backlog | Option на доске Flask Blog |
|----------------|----------------------------|
| `open` | Backlog |
| `in_progress` | In progress |
| `in_review` | In review |
| `done` | Done |

Правило статусов агента: [`.cursor/rules/backlog-status.mdc`](../.cursor/rules/backlog-status.mdc).

После merge task-PR в `dev`: агент в том же turn ставит `done`, sync, удаляет секцию из `Backlog.md` и **сразу** squash-merge docs-PR (skill [`flask-blog-git-merged-archive`](../.cursor/skills/flask-blog-git-merged-archive/SKILL.md)) — иначе на `dev` остаётся «закрытая» секция и растут конфликты при параллельных правках backlog.

### Priority → `**Приоритет:**`

Фактические опции доски №6: **`P0`**, **`P1`**, **`P2`**.

| Смысл (из обзоров / планирования) | Option |
|-----------------------------------|--------|
| Критично / высокий security | `P0` |
| Важно, не блокирует прод сразу | `P1` |
| Низкий / продукт «когда понадобится» | `P2` |

В markdown: `**Приоритет:** P0` (или `**Priority:** P0`). Конфиг: `priorityMap` в `.github/backlog.json` (обычно identity `P0`→`P0`).

### Категории и подзадачи

- **Категория** — метаданные в секции (`**Категория:** Auth / Security`); sync не создаёт отдельный field (на доске можно фильтровать Labels).
- **Подзадачи** — чеклист в `### Acceptance criteria` / `### Подзадачи` внутри `##` задачи (скрипт синхронизирует одну issue на один `##` заголовок).

---

## 8. Ограничения API

- Add item и update field — **разные** вызовы.
- Assignees/Labels/Milestone — через Issue API, не Project field mutation.
- Items без прав доступа → тип `REDACTED`.
- `gh project item-list --limit` до **500**; больше — пагинация GraphQL/`after`.
- Classic Projects API — не использовать.
- Sync skill делает только **push** markdown → GitHub (не pull Status с доски в файл).
- Нужен scope `project`; без него CLI падает на project-командах.

---

## 9. Практические команды для этого репо

```bash
gh project view 6 --owner discipleartem --format json
gh project field-list 6 --owner discipleartem --format json
gh project item-list 6 --owner discipleartem --format json --limit 50

python ~/.cursor/skills/backlog-github-projects-sync/scripts/sync_backlog.py --dry-run
python ~/.cursor/skills/backlog-github-projects-sync/scripts/sync_backlog.py --rate-limit
python ~/.cursor/skills/backlog-github-projects-sync/scripts/sync_backlog.py --pending-status
python ~/.cursor/skills/backlog-github-projects-sync/scripts/sync_backlog.py
# exit 2 = GraphQL rate limit / low budget → pending в ~/.cache/… ; после resetAt снова sync
```
