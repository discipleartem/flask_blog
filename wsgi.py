# wsgi.py — точка входа для PythonAnywhere
# Путь в настройках PA: /home/<username>/flask_blog/wsgi.py
from app import create_app
import getpass
import sys

# Получаем имя пользователя текущего процесса (надёжнее, чем os.environ)
username = getpass.getuser()

project_home = f"/home/{username}/flask_blog"
if project_home not in sys.path:
    sys.path.insert(0, project_home)


application = create_app()
