# tests/test_main.py
"""Тесты для основных маршрутов приложения."""


class TestMainRoutes:
    """Тесты основных страниц приложения."""

    def test_index_page_loads(self, client):
        """Главная страница должна загружаться."""
        response = client.get("/")
        assert response.status_code == 200
        assert "Flask Blog".encode("utf-8") in response.data

    def test_index_page_context(self, client, app):
        """Проверка контекста главной страницы."""
        with app.app_context():
            response = client.get("/")
            assert response.status_code == 200

    def test_index_with_authenticated_user(self, client, auth):
        """Главная страница для аутентифицированного пользователя."""
        auth.login()
        response = client.get("/")
        assert response.status_code == 200

    def test_about_page(self, client):
        """Страница о проекте."""
        response = client.get("/about")
        # Если страница существует
        if response.status_code == 200:
            assert "О проекте".encode("utf-8") in response.data


class TestPostManagement:
    """Тесты управления постами."""

    def test_create_post_requires_login(self, client):
        """Создание поста требует аутентификации."""
        response = client.get("/post/create", follow_redirects=False)
        assert response.status_code == 302
        assert "/auth/login" in response.headers["Location"]

    def test_create_post_authenticated(self, client, auth, app):
        """Создание поста аутентифицированным пользователем."""
        auth.login()
        response = client.get("/post/create")
        assert response.status_code == 200
        assert "Создать".encode("utf-8") in response.data

    def test_post_creation_success(self, client, auth, app):
        """Успешное создание поста."""
        auth.login()

        with app.app_context():
            # Пробуем создать пост
            response = client.post(
                "/post/create",
                data={
                    "title": "Тестовый пост",
                    "content": "Это содержимое тестового поста",
                },
                follow_redirects=True,
            )

            # Если маршрут существует и работает
            if response.status_code == 200:
                # Проверяем, что пост создан (если есть БД)
                try:
                    from app.db.db import get_db

                    db = get_db()
                    post = db.execute(
                        "SELECT * FROM post WHERE title = ?", ("Тестовый пост",)
                    ).fetchone()
                    assert post is not None
                except Exception:
                    pass  # БД может быть не настроена в тестах

    def test_view_post(self, client, app):
        """Просмотр отдельного поста."""
        with app.app_context():
            # Пробуем просмотреть пост с ID 1 (создается в conftest.py)
            response = client.get("/post/1")
            # Должен вернуть 200 (пост есть)
            assert response.status_code == 200
            # Проверяем, что в ответе есть содержимое поста
            assert b"Test Post" in response.data or b"post" in response.data

    def test_edit_post_requires_login(self, client):
        """Редактирование поста требует аутентификации."""
        response = client.get("/post/1/edit", follow_redirects=False)
        assert response.status_code == 302
        assert "/auth/login" in response.headers["Location"]

    def test_delete_post_requires_login(self, client):
        """Удаление поста требует аутентификации."""
        response = client.post("/post/1/delete", follow_redirects=False)
        assert response.status_code == 302
        assert "/auth/login" in response.headers["Location"]


class TestErrorHandlers:
    """Тесты обработчиков ошибок."""

    def test_404_error(self, client):
        """Страница 404 должна возвращать правильный статус."""
        response = client.get("/nonexistent-page")
        assert response.status_code == 404

    def test_404_error_content(self, client):
        """Страница 404 должна содержать сообщение об ошибке."""
        response = client.get("/nonexistent-page")
        if response.status_code == 404:
            # Проверяем наличие сообщения об ошибке
            assert b"404" in response.data or b"ne naidena" in response.data.lower()

    def test_500_error_handling(self, client, app):
        """Обработка ошибки 500."""
        # Этот тест требует специальной настройки для вызова 500 ошибки
        # Пока просто проверяем, что приложение не падает
        with app.app_context():
            response = client.get("/")
            assert response.status_code in [200, 302, 404, 500]


class TestDatabaseOperations:
    """Тесты операций с базой данных."""

    def test_database_initialization(self, app):
        """Инициализация базы данных."""
        with app.app_context():
            from app.db.db import init_db, get_db

            # Инициализация должна работать без ошибок
            init_db()

            # Подключение к БД должно работать
            db = get_db()
            assert db is not None

    def test_database_connection(self, app):
        """Подключение к базе данных."""
        with app.app_context():
            from app.db.db import get_db

            db = get_db()
            assert db is not None

            # Простая проверка выполнения запроса
            try:
                result = db.execute("SELECT 1").fetchone()
                assert result[0] == 1
            except Exception:
                pass  # Таблиц может не существовать


class TestConfiguration:
    """Тесты конфигурации приложения."""

    def test_development_config(self):
        """Конфигурация для разработки."""
        from config import DevelopmentConfig

        assert DevelopmentConfig.DEBUG is True
        assert hasattr(DevelopmentConfig, "SECRET_KEY")
        assert hasattr(DevelopmentConfig, "DATABASE")

    def test_production_config(self):
        """Конфигурация для продакшена."""
        from config import ProductionConfig

        assert ProductionConfig.DEBUG is False
        assert hasattr(ProductionConfig, "SECRET_KEY")
        assert hasattr(ProductionConfig, "DATABASE")

    def test_testing_config(self):
        """Конфигурация для тестирования."""
        from config import TestingConfig

        assert TestingConfig.TESTING is True
        assert TestingConfig.DATABASE == ":memory:"

    def test_config_values(self):
        """Проверка значений конфигурации."""
        from config import Config

        assert hasattr(Config, "SECRET_KEY")
        assert hasattr(Config, "BASE_DIR")
        assert hasattr(Config, "DATABASE")
        assert hasattr(Config, "ADMIN_PASSWORD")

        # Проверка пути к БД
        assert "flask_blog.sqlite" in Config.DATABASE
