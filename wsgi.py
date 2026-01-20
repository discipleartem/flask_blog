# wsgi.py — точка входа для PythonAnywhere
# Путь в настройках PA: /home/<username>/flask_blog/wsgi.py

import sys

# Укажите ваше реальное имя пользователя PythonAnywhere
PYTHONANYWHERE_USERNAME = "discipleartem"  # ← Замените на реальное!

project_home = f"/home/{PYTHONANYWHERE_USERNAME}/flask_blog"
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Импортируем фабрику приложения
from app import create_app

# Создаём экземпляр приложения
application = create_app()
