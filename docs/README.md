# Документация flask_blog

Вход для агента: [`../AGENTS.md`](../AGENTS.md) (роутер: тип задачи → файлы). Не читать весь каталог сразу.

| Файл | Когда открывать |
|------|-----------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Scoping: слои, маршруты, схема, права, карта `app/` |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Локальный запуск, UI, контент/Markdown, IronBee, проверки |
| [DEPLOY.md](DEPLOY.md) | PythonAnywhere, `.env` на проде, auto-deploy |
| [RELEASE.md](RELEASE.md) | Релиз `dev`→`main`: PR, squash, GitHub Release, sync |
| [github-releases-api.md](github-releases-api.md) | GitHub REST API Releases: endpoints, поля, `gh` |
| [Backlog.md](Backlog.md) | Активные задачи (не история) |
| [CHANGELOG.md](CHANGELOG.md) | История изменений |
| [GITHUB-PROJECTS-API.md](GITHUB-PROJECTS-API.md) | GitHub Projects v2: возможности, GraphQL/REST, маппинг backlog |

Ограничения стека (агент): [`.cursor/rules/00-project.mdc`](../.cursor/rules/00-project.mdc).  
После реализации задачи агент **автоматически** обновляет docs (skill [flask-blog-docs-after-task](../.cursor/skills/flask-blog-docs-after-task/SKILL.md); pointer в `00-project.mdc`; hook `stop`).
