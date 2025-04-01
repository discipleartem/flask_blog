from app import create_app
import logging
from logging.handlers import RotatingFileHandler


app = create_app(prod_config=True)

# логирование в файл
if not app.debug: # если не в режиме отладки
    file_handler = RotatingFileHandler('logs/flask_blog.log', maxBytes=10240, backupCount=10)
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)


if __name__ == '__main__':
    app.run()
