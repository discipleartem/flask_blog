# Deploy on PythonAnywhere

## 1. Код

```bash
# Bash console на PA
git clone https://github.com/discipleartem/flask_blog.git
cd flask_blog
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Либо `pip install -e .` если editable install доступен.

## 2. Переменные окружения

В Web → WSGI configuration / или в коде перед импортом:

```bash
export SECRET_KEY='generate-a-long-random-string'
export ADMIN_PASSWORD='your-strong-admin-password'
export DATABASE='/home/YOUR_USERNAME/flask_blog/instance/blog.sqlite3'
```

Создайте каталог БД:

```bash
mkdir -p instance
source .venv/bin/activate
flask --app wsgi db-upgrade
```

## 3. WSGI-файл (PythonAnywhere)

В панели Web → WSGI configuration file примерно так:

```python
import sys
from pathlib import Path

project = Path("/home/YOUR_USERNAME/flask_blog")
sys.path.insert(0, str(project))

# Activate venv site-packages
activate = project / ".venv" / "lib" / "python3.12" / "site-packages"
sys.path.insert(0, str(activate))

from app import create_app

application = create_app()
```

Либо укажите `wsgi.py`: `application` можно экспортировать как alias:

```python
from wsgi import app as application
```

## 4. Static files

В Web → Static files:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/YOUR_USERNAME/flask_blog/app/static` |

## 5. Smoke-чеклист после деплоя

- [ ] `GET /` открывается, виден бренд «Flask Blog»
- [ ] Переключатель темы (солнце/луна) меняет `data-bs-theme` и переживает reload
- [ ] Логин `admin#0001` с `ADMIN_PASSWORD`
- [ ] Регистрация обычного пользователя (не `admin`)
- [ ] Создание статьи → появляется на главной
- [ ] Комментарий под статьёй
- [ ] Редактирование/удаление своей статьи
- [ ] Admin: `/users/` список пользователей

## 6. Обновление

```bash
cd ~/flask_blog
git pull
source .venv/bin/activate
pip install -r requirements.txt
flask --app wsgi db-upgrade
# Reload web app в панели PA
```
