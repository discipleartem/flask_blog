# This file contains the WSGI configuration required to serve up your
# web application at http://discipleartem.pythonanywhere.com/
# It works by setting the variable 'application' to a WSGI handler of some
# description.

import sys
import getpass

# Получаем имя пользователя текущего процесса (надёжнее, чем os.environ)
username = getpass.getuser()

# Добавляем директорию проекта в sys.path
project_home = f"/home/{username}/flask_blog"
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Импортируем Flask приложение
# Переменная должна называться 'application' для WSGI
from app import create_app

application = create_app()
