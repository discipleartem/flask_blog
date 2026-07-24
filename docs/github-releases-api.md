# GitHub Releases API (REST)

Краткая справка для агентов flask_blog. Канон процесса релиза: [`RELEASE.md`](RELEASE.md).  
Создание Release в репо: skill [`flask-blog-git-release`](../.cursor/skills/flask-blog-git-release/SKILL.md).

Официально:

- [REST: Releases](https://docs.github.com/en/rest/releases/releases)
- [REST: Release assets](https://docs.github.com/en/rest/releases/assets)
- [CLI: `gh release create`](https://cli.github.com/manual/gh_release_create)

Заголовки (типично): `Authorization: Bearer <TOKEN>`, `Accept: application/vnd.github+json`, `X-GitHub-Api-Version` (актуальная версия — в docs GitHub).

---

## 1. Endpoints

| Действие | Метод | Путь |
|----------|-------|------|
| List releases | `GET` | `/repos/{owner}/{repo}/releases` |
| Create release | `POST` | `/repos/{owner}/{repo}/releases` |
| Generate notes (без сохранения) | `POST` | `/repos/{owner}/{repo}/releases/generate-notes` |
| Latest published | `GET` | `/repos/{owner}/{repo}/releases/latest` |
| By tag | `GET` | `/repos/{owner}/{repo}/releases/tags/{tag}` |
| By id | `GET` | `/repos/{owner}/{repo}/releases/{release_id}` |
| Update | `PATCH` | `/repos/{owner}/{repo}/releases/{release_id}` |
| Delete | `DELETE` | `/repos/{owner}/{repo}/releases/{release_id}` |
| List assets | `GET` | `/repos/{owner}/{repo}/releases/{release_id}/assets` |
| Upload asset | `POST` | `https://uploads.github.com/repos/{owner}/{repo}/releases/{release_id}/assets?name=` |
| Get / update / delete asset | `GET`/`PATCH`/`DELETE` | `/repos/{owner}/{repo}/releases/assets/{asset_id}` |

List **не** включает обычные git-теги без Release. Drafts в list видят только пользователи с push.

---

## 2. Create release — поля body

`POST /repos/{owner}/{repo}/releases`

| Поле | API | В flask_blog при «релиз» |
|------|-----|--------------------------|
| `tag_name` | **обязателен** | версия с `v`, напр. `v0.4.0` |
| `target_commitish` | опционален (default = default branch) | **всегда** `main` |
| `name` | опционален | **всегда** человекочитаемый title (напр. `Flask Blog 0.4.0`) |
| `body` | опционален | **всегда** из секции `docs/CHANGELOG.md` для версии |
| `draft` | bool, default `false` | **явно** `false` (published), иначе `true` только по запросу |
| `prerelease` | bool, default `false` | **явно** `false`, иначе `true` только по запросу |
| `generate_release_notes` | bool, default `false` | опционально `true`: auto-notes; если задан `body`, он **prepend** к auto |
| `make_latest` | `"true"` \| `"false"` \| `"legacy"`, default `"true"` | `"true"` для обычного релиза; drafts/prereleases не могут быть latest |
| `discussion_category_name` | string | не использовать, пока в репо нет Discussions category |

**Правило проекта:** при командах «релиз» / «релиз в main» не полагаться на defaults API/CLI — **заполнить все поля** из таблицы (включая явные `draft` / `prerelease` / `target` / `name` / `body`).

Права: push в репо. Если `target_commitish` указывает на коммит, меняющий `.github/workflows/`, токену нужен scope `workflow` / permission Workflows (write); иначе часто **404** или **403**.

---

## 3. Generate release notes

`POST /repos/{owner}/{repo}/releases/generate-notes` — **не** создаёт Release; возвращает `{ "name", "body" }`.

| Поле | Назначение |
|------|------------|
| `tag_name` | **обязателен** |
| `target_commitish` | нужен, если тега ещё нет |
| `previous_tag_name` | явное начало диапазона notes |
| `configuration_file_path` | иначе `.github/release.yml` / default |

В CLI: `gh release create … --generate-notes` (+ `--notes` / `-F` prepend).

Для flask_blog предпочтение: **body из CHANGELOG**; `--generate-notes` — дополнение, не замена, если CHANGELOG уже подготовлен.

---

## 4. Ответы и ошибки

| Код | Когда |
|-----|--------|
| **201** | Create OK (`html_url`, `upload_url`, `id`, `tag_name`, …) |
| **200** | Get / list / update / generate-notes |
| **204** | Delete |
| **404** | Нет ресурса; неверная discussion category; workflow-permission edge case |
| **401** | Нет/битый auth |
| **403** | Нет доступа (в т.ч. integration / workflows) |
| **422** | Validation / spam / дубликат asset name при upload |

Вторичный rate limit — при частых create (notifications).

Ключевые поля ответа Release: `id`, `tag_name`, `target_commitish`, `name`, `body`, `draft`, `prerelease`, `html_url`, `upload_url`, `tarball_url`, `zipball_url`, `assets[]`.

---

## 5. Assets

- Upload: host **`uploads.github.com`**, raw binary body, query `name=` (обязателен), опционально `label=`.
- URL берётся из `upload_url` ответа create (hypermedia).
- Дубликат имени файла → **422**; пустой asset после сбоя upload можно удалить.
- Скачать бинарь: `Accept: application/octet-stream` или `browser_download_url`.

Для flask_blog (PythonAnywhere / source deploy) assets обычно **не нужны** — достаточно tag + notes.

---

## 6. CLI ↔ API

| Цель | `gh` | REST |
|------|------|------|
| Создать | `gh release create <tag> …` | `POST …/releases` |
| Notes из файла | `-F path` / `-n` | `body` |
| Title | `-t` / `--title` | `name` |
| Target | `--target main` | `target_commitish` |
| Draft | `--draft` | `draft: true` |
| Prerelease | `--prerelease` | `prerelease: true` |
| Latest | `--latest` / `--latest=false` | `make_latest` |
| Auto notes | `--generate-notes` | `generate_release_notes: true` |
| Проверка | `gh release view <tag>` | `GET …/releases/tags/{tag}` |

Пример (все поля явно — канон проекта):

```bash
TAG=v0.4.0
gh release create "$TAG" \
  --title "Flask Blog 0.4.0" \
  --notes-file /tmp/release-body.md \
  --target main \
  --latest
# без --draft и без --prerelease → published full release
```

Эквивалент через API:

```bash
gh api repos/{owner}/{repo}/releases -f tag_name="$TAG" \
  -f target_commitish=main \
  -f name="Flask Blog 0.4.0" \
  -f body="$(cat /tmp/release-body.md)" \
  -F draft=false \
  -F prerelease=false \
  -F generate_release_notes=false \
  -f make_latest=true
```
