# Backlog

Список будущих задач проекта. Подход к реализации выбирается при взятии задачи в работу.

Синхронизация с [GitHub Project «Flask Blog»](https://github.com/users/discipleartem/projects/6): `python ~/.cursor/skills/backlog-github-projects-sync/scripts/sync_backlog.py` (конфиг [`.github/backlog.json`](../.github/backlog.json)).

## Улучшение UI при регистрации/авторизации

**Статус:** in_progress
**GitHub:** #39

### Проблема

При регистрации пользователь вводит только имя (`name`). Discriminator (`#NNNN`) назначается на сервере после POST. Поле регистрации помечено как `autocomplete="username"`, поэтому браузерный менеджер паролей предлагает сохранить логин **без** дискриминатора.

На странице входа требуется полный тег `username#0001`. После logout autofill подставляет неполный логин. Запомнить дискриминатор нереально — пользователь не может войти.

### Acceptance criteria

- После регистрации браузер / password manager получает (или может сохранить) полный логин в формате `name#NNNN`.
- После logout → login autofill (или сохранённая учётка) позволяет войти без ручного вспоминания discriminator.
- Формат входа `name#NNNN` и модель `UNIQUE(name, discriminator)` не ломаются.
- Поведение проверено вручную в браузере (не только по коду и unit-тестам).
