from app import create_app
from dotenv import load_dotenv

app = create_app(prod_config=True)

# Загрузка переменных окружения из файла .env
load_dotenv()

if __name__ == '__main__':
    app.run()

# проверка хука