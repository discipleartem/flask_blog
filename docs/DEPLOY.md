# Deploy on PythonAnywhere (тариф Beginner)

Официально: [PythonAnywhere](https://www.pythonanywhere.com/), [тарифы](https://www.pythonanywhere.com/pricing/),
[возможности free/Beginner](https://help.pythonanywhere.com/pages/FreeAccountsFeatures/),
[деплой Flask](https://help.pythonanywhere.com/pages/Flask/).

Сайт на free-плане: `https://YOUR_USERNAME.pythonanywhere.com/`  
Пример: `https://discipleartem.pythonanywhere.com/`

## Совместимость (наш проект)

| Компонент | Версия |
|-----------|--------|
| Python | **3.12** |
| Flask | **3.0.3** |

Для Python 3.12 на PA ставьте только `Flask==3.0.3` (`requirements.txt` / `pyproject.toml`). Flask 3.1+ на этом окружении не используем.

## Ограничения тарифа Beginner (free)

По [Free Accounts Features](https://help.pythonanywhere.com/pages/FreeAccountsFeatures/) и [Pricing](https://www.pythonanywhere.com/pricing/):

| Ограничение | Beginner |
|-------------|----------|
| Стоимость | $0 / месяц |
| Web apps | **1** приложение, **1** web worker |
| Домен | только `USERNAME.pythonanywhere.com` (свой домен — на платных планах) |
| Срок жизни web app | истекает после **1 месяца бездействия** (нужно продлевать / заходить на сайт) |
| Consoles | до **2** одновременно (Bash / Python) |
| Диск | **512 MiB** |
| CPU | **100 CPU-секунд** в сутки |
| Bandwidth | низкий (Low) |
| Исходящий интернет из кода | только **whitelist** сайтов, **HTTP(S)** |
| SSH | **нет** (работа через Web UI + Bash console) |
| MySQL | **нет** у новых free-аккаунтов после янв. 2026 (нам не нужен — SQLite) |
| Scheduled / always-on tasks | **нет** у новых free-аккаунтов после янв. 2026 |
| Поддержка | community (форумы / help), не прямая поддержка PA |

Аккаунты, созданные **до** 2026-01-15 (US) / 2026-01-08 (EU), могут ещё иметь MySQL и 1 daily task — см. [анонс](https://blog.pythonanywhere.com/221/).

### Что это значит для Flask Blog

- SQLite-файл держите в home (`instance/`) — укладывайтесь в 512 MiB вместе с `.venv` и клоном репо.
- Не рассчитывайте на фоновые cron-задачи на Beginner.
- CDN Bootstrap/Fonts грузятся **в браузере у посетителя**, не с сервера PA — ок для whitelist.
- `git clone` / `git pull` с GitHub обычно работают из Bash (HTTPS).

---

## Способ деплоя: Manual configuration + virtualenv

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

python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -c "from importlib.metadata import version; print(version('flask'))"  # 3.0.3

mkdir -p instance
export SECRET_KEY='generate-a-long-random-string'
export ADMIN_PASSWORD='your-strong-admin-password'
export DATABASE="$HOME/flask_blog/instance/blog.sqlite3"
flask --app wsgi db-upgrade
```

Альтернатива venv через `virtualenvwrapper` (`mkvirtualenv`), как в [доке PA](https://help.pythonanywhere.com/pages/Flask/) — тогда в Web tab укажите путь к этому env.

### Шаг 2. Web app (Manual configuration)

Web → **Add a new web app** → **Manual configuration** → **Python 3.12**.

В секции **Virtualenv** укажите путь к venv, например:

```text
/home/YOUR_USERNAME/flask_blog/.venv
```

Пример для аккаунта `discipleartem`:

```text
/home/discipleartem/flask_blog/.venv
```

### Шаг 3. WSGI-файл

Ссылка **WSGI configuration file** в Web tab. Замените содержимое на:

```python
import os
import sys
from pathlib import Path

project = Path("/home/YOUR_USERNAME/flask_blog")
sys.path.insert(0, str(project))

# site-packages из venv (если Virtualenv в UI не подхватился)
venv_site = project / ".venv" / "lib" / "python3.12" / "site-packages"
sys.path.insert(0, str(venv_site))

os.environ.setdefault("SECRET_KEY", "change-me-in-production")
os.environ.setdefault("ADMIN_PASSWORD", "change-me-admin")
os.environ.setdefault(
    "DATABASE",
    str(project / "instance" / "blog.sqlite3"),
)

from app import create_app

application = create_app()
```

Подставьте свой `YOUR_USERNAME` (например `discipleartem`).

Важно ([документация PA](https://help.pythonanywhere.com/pages/Flask/)):

- WSGI должен экспортировать **`application`**, не вызывать `app.run()`.
- У нас `app.run()` нет — точка входа `wsgi.py` / `create_app()` безопасны для импорта.

### Шаг 4. Static files

Web → Static files:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/YOUR_USERNAME/flask_blog/app/static` |

### Шаг 5. Reload

Кнопка зелёная **Reload** на вкладке Web. Откройте `https://YOUR_USERNAME.pythonanywhere.com/`.

---

## Smoke-чеклист

- [ ] Главная `/` — бренд «Flask Blog»
- [ ] Тема light/dark (солнце/луна) переживает reload
- [ ] Логин `admin#0001` + `ADMIN_PASSWORD`
- [ ] Регистрация пользователя (не `admin`)
- [ ] Создание статьи и комментария
- [ ] Admin: `/users/`
- [ ] После простоя ~месяца — проверить, что web app не истёк (Beginner)

## Обновление кода

```bash
cd ~/flask_blog
git pull
source .venv/bin/activate
pip install -r requirements.txt
python -c "from importlib.metadata import version; assert version('flask') == '3.0.3'"
flask --app wsgi db-upgrade
# Web → Reload
```

## Частые ошибки

| Симптом | Что проверить |
|---------|----------------|
| 502 / 504 | traceback в Web → Log files; не вызывается ли `app.run()` |
| ModuleNotFoundError | путь Virtualenv / `sys.path` в WSGI, Python **3.12** |
| Неверный Flask | `pip show flask` → должен быть **3.0.3** |
| Перезаписан чужой `flask_app.py` | выбрали Quickstart Flask — пересоздайте app через **Manual configuration** |
| Нет места на диске | 512 MiB: удалите лишние `__pycache__`, старые venv, большие логи |
