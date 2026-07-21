# Deploy on PythonAnywhere (тариф Beginner)

Официально: [PythonAnywhere](https://www.pythonanywhere.com/), [тарифы](https://www.pythonanywhere.com/pricing/),
[возможности free/Beginner](https://help.pythonanywhere.com/pages/FreeAccountsFeatures/),
[деплой Flask](https://help.pythonanywhere.com/pages/Flask/),
[API](https://help.pythonanywhere.com/pages/API/).

Сайт на free-плане: `https://YOUR_USERNAME.pythonanywhere.com/`  
Пример: `https://discipleartem.pythonanywhere.com/`

**После первичной настройки** код на прод обновляется **автоматически** при merge/push в `main`
(GitHub Actions → hook на PA → reload). См. [Auto-deploy через GitHub](#auto-deploy-через-github).

## Совместимость (наш проект)


| Компонент     | Версия    |
| ------------- | --------- |
| Python        | **3.12**  |
| Flask         | **3.0.3** |
| python-dotenv | **1.2.2** |


Для Python 3.12 на PA ставьте только `Flask==3.0.3` (`requirements.txt` / `pyproject.toml`). Flask 3.1+ на этом окружении не используем.

## Ограничения тарифа Beginner (free)

По [Free Accounts Features](https://help.pythonanywhere.com/pages/FreeAccountsFeatures/) и [Pricing](https://www.pythonanywhere.com/pricing/):


| Ограничение                 | Beginner                                                                      |
| --------------------------- | ----------------------------------------------------------------------------- |
| Стоимость                   | $0 / месяц                                                                    |
| Web apps                    | **1** приложение, **1** web worker                                            |
| Домен                       | только `USERNAME.pythonanywhere.com` (свой домен — на платных планах)         |
| Срок жизни web app          | истекает после **1 месяца бездействия** (нужно продлевать / заходить на сайт) |
| Consoles                    | до **2** одновременно (Bash / Python)                                         |
| Диск                        | **512 MiB**                                                                   |
| CPU                         | **100 CPU-секунд** в сутки                                                    |
| Bandwidth                   | низкий (Low)                                                                  |
| Исходящий интернет из кода  | только **whitelist** сайтов, **HTTP(S)**                                      |
| SSH                         | **нет** (работа через Web UI + Bash console)                                  |
| MySQL                       | **нет** у новых free-аккаунтов после янв. 2026 (нам не нужен — SQLite)        |
| Scheduled / always-on tasks | **нет** у новых free-аккаунтов после янв. 2026                                |
| Поддержка                   | community (форумы / help), не прямая поддержка PA                             |


Аккаунты, созданные **до** 2026-01-15 (US) / 2026-01-08 (EU), могут ещё иметь MySQL и 1 daily task — см. [анонс](https://blog.pythonanywhere.com/221/).

### Что это значит для Flask Blog

- SQLite-файл держите в home (`instance/`) — укладывайтесь в 512 MiB вместе с `.venv` и клоном репо.
- Не рассчитывайте на фоновые cron-задачи на Beginner.
- CDN Bootstrap/Fonts грузятся **в браузере у посетителя**, не с сервера PA — ок для whitelist.
- `git clone` / `git pull` с GitHub обычно работают из Bash (HTTPS).
- SSH с GitHub Actions на PA **недоступен** — поэтому auto-deploy идёт через HTTP-hook + [API reload](https://help.pythonanywhere.com/pages/API/).

---



## Первичная настройка: Manual configuration + virtualenv

Для **уже существующего** проекта (наш репозиторий) нужен путь **Manual configuration**, а не «Quickstart new Flask project».

Quickstart Flask создаёт/перезаписывает файл вроде `/home/USERNAME/mysite/flask_app.py` — это заглушка PA, **не** наш код. В мастере Web → Add a new web app выбирайте:

1. **Manual configuration** (не Flask quickstart)
2. Python **3.12**

Официальная инструкция: [Setting up Flask on PythonAnywhere](https://help.pythonanywhere.com/pages/Flask/).

### Шаг 1. Клон и зависимости (Bash console)

Consoles → Bash (на Beginner максимум 2 консоли):

```bash
cd ~
git clone https://github.com/discipleartem/flask_blog.git
cd flask_blog
git checkout main

python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -c "from importlib.metadata import version; print(version('flask'))"  # 3.0.3

mkdir -p instance
cp .env.example .env
nano .env   # или vim: заполните SECRET_KEY, ADMIN_PASSWORD, DATABASE, DEPLOY_SECRET
flask --app wsgi db-upgrade
```

Клон **обязательно** на ветке `main` — auto-deploy делает `git pull origin main`.

### Шаг 2. Файл `.env` на сервере

Шаблон в репозитории: [`.env.example`](../.env.example). Реальный `.env` **не коммитится**.

```env
SECRET_KEY=generate-a-long-random-string
ADMIN_PASSWORD=your-strong-admin-password
DATABASE=/home/YOUR_USERNAME/flask_blog/instance/blog.sqlite3
DEPLOY_SECRET=generate-another-long-random-string
SESSION_COOKIE_SECURE=1
```


| Переменная              | Назначение                                                                              |
| ----------------------- | --------------------------------------------------------------------------------------- |
| `SECRET_KEY`            | Подпись session cookie Flask                                                            |
| `ADMIN_PASSWORD`        | Пароль `admin#0001` при seed БД                                                         |
| `DATABASE`              | Абсолютный путь к SQLite                                                                |
| `DEPLOY_SECRET`         | Bearer-токен для `POST /internal/deploy` (auto-deploy). Пусто = endpoint выключен (404) |
| `SESSION_COOKIE_SECURE` | `1` на HTTPS (PythonAnywhere); `0`/пусто для локального `http://`                       |


`load_dotenv` читает `.env` при старте (`app/config.py`). По умолчанию **python-dotenv не перезаписывает** переменные, которые уже есть в окружении процесса (`os.environ`).

| Ситуация | Что получит приложение |
|----------|------------------------|
| Переменная задана только в `.env` | Значение из `.env` |
| Переменная уже есть в окружении (export, WSGI, systemd, панель PA «Environment variables») **и** есть в `.env` | Значение из **окружения**; строка в `.env` для этого ключа **игнорируется** |
| Переменной нет ни в окружении, ни в `.env` | Дефолт из `Config` в `app/config.py` (например `SECRET_KEY=dev-change-me`) |

Практически: если на сервере один раз экспортировали `SECRET_KEY=old`, а в `.env` написали новый ключ — приложение продолжит брать `old`, пока не уберёте переменную из окружения или не перезапустите процесс без неё. Менять секреты удобнее **только в `.env`** (и не дублировать те же имена в окружении WSGI/shell), либо наоборот — только в панели окружения, без копии в `.env`.

Сгенерировать секреты (в Bash на PA или локально):

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

Альтернатива venv через `virtualenvwrapper` (`mkvirtualenv`), как в [доке PA](https://help.pythonanywhere.com/pages/Flask/) — тогда в Web tab укажите путь к этому env.

### Шаг 3. Web app (Manual configuration)

Web → **Add a new web app** → **Manual configuration** → **Python 3.12**.

В секции **Virtualenv** укажите путь к venv, например:

```text
/home/YOUR_USERNAME/flask_blog/.venv
```

Пример для аккаунта `discipleartem`:

```text
/home/discipleartem/flask_blog/.venv
```



### Шаг 4. WSGI-файл

Ссылка **WSGI configuration file** в Web tab. Замените содержимое на:

```python
import sys
from pathlib import Path

project = Path("/home/YOUR_USERNAME/flask_blog")
sys.path.insert(0, str(project))

# site-packages из venv (если Virtualenv в UI не подхватился)
venv_site = project / ".venv" / "lib" / "python3.12" / "site-packages"
sys.path.insert(0, str(venv_site))

from app import create_app

application = create_app()
```

Подставьте свой `YOUR_USERNAME` (например `discipleartem`). Секреты — **только** в `~/flask_blog/.env`, не в WSGI.

Важно ([документация PA](https://help.pythonanywhere.com/pages/Flask/)):

- WSGI должен экспортировать `application`, не вызывать `app.run()`.
- У нас `app.run()` нет — точка входа `wsgi.py` / `create_app()` безопасны для импорта.



### Шаг 5. Static files

Web → Static files:


| URL        | Directory                                   |
| ---------- | ------------------------------------------- |
| `/static/` | `/home/YOUR_USERNAME/flask_blog/app/static` |




### Шаг 6. Reload

Кнопка зелёная **Reload** на вкладке Web. Откройте `https://YOUR_USERNAME.pythonanywhere.com/`.

Дальше — [Smoke-чеклист](#smoke-чеклист) и [Auto-deploy через GitHub](#auto-deploy-через-github).

---



## Smoke-чеклист

- [ ] Главная `/` — бренд «Flask Blog»
- [ ] Тема light/dark (солнце/луна) переживает reload
- [ ] Логин `admin#0001` + `ADMIN_PASSWORD`
- [ ] Регистрация пользователя (не `admin`)
- [ ] Создание статьи и комментария
- [ ] Admin: `/users/`
- [ ] `POST /internal/deploy` без Bearer → **401** (или **404**, если `DEPLOY_SECRET` пуст)
- [ ] После простоя ~месяца — проверить, что web app не истёк (Beginner)

---



## Auto-deploy через GitHub

Цель: релиз `dev` **→** `main` на GitHub сам выкатывает код на PythonAnywhere без ручного `git pull` и кнопки Reload.

Workflow: [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml).

### Как это работает

```text
  PR / squash-merge в main
            │
            ▼
  GitHub Actions (push: main) — deploy.yml
            │
            ├─ 0. unittest (Python 3.12); при падении deploy не запускается
            │
            ├─ 1. POST https://PA_DOMAIN/internal/deploy
            │      Authorization: Bearer DEPLOY_SECRET
            │      на PA: git pull origin main
            │             .venv/bin/pip install -r requirements.txt
            │             .venv/bin/flask --app wsgi db-upgrade
            │
            └─ 2. POST PA API …/webapps/PA_DOMAIN/reload/
                   Authorization: Token PA_API_TOKEN
                   worker подхватывает новый код
```

Отдельно CI без деплоя: [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) на `push`/`pull_request` в `main` и `dev`.

Триггеры workflow:


| Событие               | Когда                                                                |
| --------------------- | -------------------------------------------------------------------- |
| `push` в ветку `main` | merge релиза `dev` → `main`, прямой push в `main`                    |
| `workflow_dispatch`   | ручной запуск: Actions → **Deploy to PythonAnywhere** → Run workflow |


Код hook: `app/deploy/` → маршрут `POST /internal/deploy`.

### Предварительные условия на PA

Перед первым auto-deploy убедитесь:

1. Первичная настройка выше уже сделана, сайт открывается.
2. Клон: `cd ~/flask_blog && git checkout main && git status` — чистое дерево, tracking `origin/main`.
3. В `.env` задан **непустой** `DEPLOY_SECRET` (тот же, что пойдёт в GitHub Secrets).
4. После правки `.env` — **Reload** webapp (иначе процесс не увидит новый секрет).
5. Из Bash на PA `git pull origin main` проходит без интерактива (публичный репо или сохранённые credentials).

Проверка hook вручную (подставьте домен и секрет):

```bash
curl -i -X POST \
  -H "Authorization: Bearer YOUR_DEPLOY_SECRET" \
  "https://YOUR_USERNAME.pythonanywhere.com/internal/deploy"
```

Ожидание: HTTP **200** и JSON `{"ok": true, "steps": [...]}`.  
Без заголовка / неверный токен → **401**. Пустой `DEPLOY_SECRET` на сервере → **404**.

### Настройка GitHub Secrets (один раз)

Репозиторий → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.


| Secret          | Значение                 | Где взять                                                      |
| --------------- | ------------------------ | -------------------------------------------------------------- |
| `DEPLOY_SECRET` | длинная случайная строка | **тот же**, что `DEPLOY_SECRET` в `.env` на PA                 |
| `PA_API_TOKEN`  | API token аккаунта PA    | PythonAnywhere → Account → **API token** → Generate            |
| `PA_USERNAME`   | логин PA                 | например `discipleartem`                                       |
| `PA_DOMAIN`     | домен webapp             | например `discipleartem.pythonanywhere.com`                    |
| `PA_HOST`       | хост API                 | см. [Как узнать `PA_HOST`](#как-узнать-pa_host)                |


#### Как узнать `PA_HOST`

Секрет должен совпадать с **регионом** аккаунта ([документация API](https://help.pythonanywhere.com/pages/API/)):

| Регион | `PA_HOST` | Типичный домен сайта |
|--------|-----------|----------------------|
| US (global) | `www.pythonanywhere.com` | `USERNAME.pythonanywhere.com` |
| EU | `eu.pythonanywhere.com` | `USERNAME.eu.pythonanywhere.com` |

**Способ 1 — URL в браузере** (когда вы залогинены в дашборд):

- адрес начинается с `https://www.pythonanywhere.com/` → `PA_HOST=www.pythonanywhere.com`
- адрес начинается с `https://eu.pythonanywhere.com/` → `PA_HOST=eu.pythonanywhere.com`

**Способ 2 — Bash console на PA:**

```bash
echo "$PYTHONANYWHERE_SITE"
```

Вывод (`www.pythonanywhere.com` или `eu.pythonanywhere.com`) — готовое значение для GitHub Secret `PA_HOST`.

Неверный `PA_HOST` → шаг Reload в Actions падает (API token «не видит» аккаунт в другом регионе).

### Релизный цикл (день за днём)

1. Фичи мержатся в `dev`, тестируются (CI `ci.yml` на PR/push).
2. PR `dev` **→** `main` (обычно squash merge) → push в `main`.
3. Actions запускает **Deploy to PythonAnywhere**: сначала job `test`, затем hook + reload.
4. В логе job `deploy`: ответ hook (JSON со `steps`) и строка `Reload requested`.
5. Откройте сайт и пробегитесь по [Smoke-чеклисту](#smoke-чеклист).

Ручной прогон без merge: Actions → **Deploy to PythonAnywhere** → **Run workflow**.

### Безопасность

- `DEPLOY_SECRET` и `PA_API_TOKEN` — только в `.env` на PA и в GitHub Secrets; **не** в git, не в WSGI, не в Issues/PR.
- Без `DEPLOY_SECRET` на сервере endpoint отвечает **404** (выключен).
- Неверный Bearer → **401** (сравнение timing-safe).
- Endpoint не логинит пароли БД; в ответе — stdout/stderr шагов деплоя (без содержимого `.env`).
- Меняли `DEPLOY_SECRET`? Обновите **и** `.env` на PA (Reload), **и** GitHub Secret.



### Откат

Авто-отката нет. Варианты:

1. Revert-коммит в `main` → снова сработает auto-deploy.
2. Вручную на PA: `git checkout <хороший-sha>` / `git reset --hard origin/main` после force на GitHub (осторожно) → Reload.
3. Временно отключить auto-deploy: очистить `DEPLOY_SECRET` в `.env` + Reload (hook → 404); workflow будет падать на шаге hook — либо отключите workflow в Actions.

---



## Обновление кода вручную (fallback)

Если Actions недоступен или нужно чинить прод без GitHub:

```bash
cd ~/flask_blog
git checkout main
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt
python -c "from importlib.metadata import version; assert version('flask') == '3.0.3'"
flask --app wsgi db-upgrade
# Web → Reload
```

---



## Частые ошибки


| Симптом                               | Что проверить                                                                                                     |
| ------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| 502 / 504                             | traceback в Web → Log files; не вызывается ли `app.run()`                                                         |
| ModuleNotFoundError                   | Virtualenv / `sys.path` в WSGI, Python **3.12**; `pip show python-dotenv`                                         |
| Неверный Flask                        | `pip show flask` → **3.0.3**                                                                                      |
| Перезаписан чужой `flask_app.py`      | Quickstart Flask — пересоздайте app через **Manual configuration**                                                |
| Нет места на диске                    | 512 MiB: `__pycache__`, старые venv, большие логи                                                                 |
| Actions: hook **401** / **404**       | `DEPLOY_SECRET` в `.env` ≡ GitHub Secret; после правки `.env` — Reload; URL = `https://PA_DOMAIN/internal/deploy` |
| Actions: hook **500**, шаг `git pull` | ветка `main`, чистое дерево, `git pull` из Bash на PA без ошибок                                                  |
| Actions: hook OK, сайт старый         | шаг Reload упал? верны ли `PA_HOST` / `PA_USERNAME` / `PA_DOMAIN` / `PA_API_TOKEN`?                               |
| Actions: API reload **не 2xx**        | токен API, регион (`www` vs `eu`), имя домена webapp без `https://`                                               |
| Workflow не стартует                  | push именно в `main`; файл `.github/workflows/deploy.yml` есть на `main`                                          |
| Web app «протух» (Beginner)           | зайти на сайт / продлить в Web tab после месяца бездействия                                                       |


