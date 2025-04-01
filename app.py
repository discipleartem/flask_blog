from app import create_app
from webhook_handler import webhook

app = create_app(prod_config=True)

# Регистрируем blueprint для webhook
app.register_blueprint(webhook)
if __name__ == '__main__':
    app.run()