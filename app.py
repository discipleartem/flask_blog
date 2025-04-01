from app import create_app

app = create_app(prod_config=True)

if __name__ == '__main__':
    app.run()
#тест хука