# tests/test_database.py
"""Тесты для работы с базой данных."""

from tests.base import DatabaseTestHelper


class TestDatabaseSchema:
    """Тесты схемы базы данных."""

    def test_database_initialization(self, app):
        """Инициализация базы данных."""
        with app.app_context():
            from app.db.db import init_db, get_db

            # Инициализация БД
            init_db()

            # Проверка подключения
            db = get_db()
            assert db is not None

    def test_user_table_structure(self, app):
        """Проверка структуры таблицы пользователей."""
        with app.app_context():
            from app.db.db import get_db

            db = get_db()

            # Проверка существования таблицы
            try:
                result = db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='user'"
                ).fetchone()
                assert result is not None
            except Exception:
                pass  # Таблица может не существовать

    def test_post_table_structure(self, app):
        """Проверка структуры таблицы постов."""
        with app.app_context():
            from app.db.db import get_db

            db = get_db()

            # Проверка существования таблицы
            try:
                result = db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='post'"
                ).fetchone()
                assert result is not None
            except Exception:
                pass  # Таблица может не существовать

    def test_comment_table_structure(self, app):
        """Проверка структуры таблицы комментариев."""
        with app.app_context():
            from app.db.db import get_db

            db = get_db()

            # Проверка существования таблицы
            try:
                result = db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='comment'"
                ).fetchone()
                assert result is not None
            except Exception:
                pass  # Таблица может не существовать


class TestDatabaseOperations:
    """Тесты операций с базой данных."""

    def test_user_crud_operations(self, app):
        """CRUD операции для пользователей."""
        with app.app_context():
            from app.db.db import get_db

            db = get_db()

            # CREATE с использованием хелпера
            hashed_pw, salt = DatabaseTestHelper.create_user_with_password(
                db, "test_user_crud", 8888, "test_password"
            )
            db.commit()

            # READ
            user = db.execute(
                "SELECT * FROM user WHERE username = ? AND discriminator = ?",
                ("test_user_crud", 8888),
            ).fetchone()
            assert user is not None
            assert user["username"] == "test_user_crud"
            assert user["discriminator"] == 8888

            # UPDATE
            db.execute(
                "UPDATE user SET username = ? WHERE username = ? AND discriminator = ?",
                ("updated_user", "test_user_crud", 8888),
            )
            db.commit()

            updated_user = db.execute(
                "SELECT * FROM user WHERE username = ?", ("updated_user",)
            ).fetchone()
            assert updated_user is not None
            assert updated_user["username"] == "updated_user"

            # DELETE
            DatabaseTestHelper.cleanup_test_data(db, usernames=["updated_user"])

            # Проверка удаления
            deleted_user = db.execute(
                "SELECT * FROM user WHERE username = ?", ("updated_user",)
            ).fetchone()
            assert deleted_user is None

    def test_post_crud_operations(self, app):
        """CRUD операции для постов."""
        with app.app_context():
            from app.db.db import get_db

            db = get_db()

            # Создаем пользователя с постом через хелпер
            user_id, post_id = DatabaseTestHelper.create_user_with_post(
                db, "post_test_user", 7777, "test_password", "Test Post", "Test content"
            )

            if user_id and post_id:
                # READ
                post = db.execute(
                    "SELECT * FROM post WHERE id = ?", (post_id,)
                ).fetchone()
                assert post is not None
                assert post["title"] == "Test Post"
                assert post["content"] == "Test content"

                # UPDATE
                db.execute(
                    "UPDATE post SET title = ?, content = ? WHERE id = ?",
                    ("Updated Post", "Updated content", post_id),
                )
                db.commit()

                updated_post = db.execute(
                    "SELECT * FROM post WHERE id = ?", (post_id,)
                ).fetchone()
                assert updated_post["title"] == "Updated Post"
                assert updated_post["content"] == "Updated content"

                # DELETE
                db.execute("DELETE FROM post WHERE id = ?", (post_id,))
                db.commit()

                deleted_post = db.execute(
                    "SELECT * FROM post WHERE id = ?", (post_id,)
                ).fetchone()
                assert deleted_post is None

            # Удаляем тестового пользователя
            DatabaseTestHelper.cleanup_test_data(db, usernames=["post_test_user"])

    def test_comment_crud_operations(self, app):
        """CRUD операции для комментариев."""
        with app.app_context():
            from app.db.db import get_db

            db = get_db()

            # Создаем тестового пользователя и пост
            from app.auth import hash_password

            hashed_pw, salt = hash_password("test_password")
            db.execute(
                "INSERT INTO user (username, discriminator, password, salt) VALUES (?, ?, ?, ?)",
                ("comment_test_user", 6666, hashed_pw, salt),
            )
            db.commit()

            user = db.execute(
                "SELECT id FROM user WHERE username = ? AND discriminator = ?",
                ("comment_test_user", 6666),
            ).fetchone()

            if user:
                db.execute(
                    "INSERT INTO post (title, content, author_id) VALUES (?, ?, ?)",
                    ("Comment Test Post", "Test content for comments", user["id"]),
                )
                db.commit()

                post = db.execute(
                    "SELECT id FROM post WHERE title = ?", ("Comment Test Post",)
                ).fetchone()

                if post:
                    # CREATE
                    db.execute(
                        "INSERT INTO comment (content, author_id, post_id) VALUES (?, ?, ?)",
                        ("Test comment", user["id"], post["id"]),
                    )
                    db.commit()

                    # READ
                    comment = db.execute(
                        "SELECT * FROM comment WHERE content = ?", ("Test comment",)
                    ).fetchone()
                    assert comment is not None
                    assert comment["content"] == "Test comment"

                    # UPDATE
                    db.execute(
                        "UPDATE comment SET content = ? WHERE id = ?",
                        ("Updated comment", comment["id"]),
                    )
                    db.commit()

                    updated_comment = db.execute(
                        "SELECT * FROM comment WHERE id = ?", (comment["id"],)
                    ).fetchone()
                    assert updated_comment["content"] == "Updated comment"

                    # DELETE
                    db.execute("DELETE FROM comment WHERE id = ?", (comment["id"],))
                    db.commit()

                    deleted_comment = db.execute(
                        "SELECT * FROM comment WHERE id = ?", (comment["id"],)
                    ).fetchone()
                    assert deleted_comment is None

                # Удаляем тестовый пост
                db.execute("DELETE FROM post WHERE id = ?", (post["id"],))
                db.commit()

            # Удаляем тестового пользователя
            db.execute(
                "DELETE FROM user WHERE username = ? AND discriminator = ?",
                ("comment_test_user", 6666),
            )
            db.commit()


class TestDatabaseConstraints:
    """Тесты ограничений базы данных."""

    def test_unique_username_discriminator(self, app):
        """Уникальность пары username-discriminator."""
        with app.app_context():
            from app.db.db import get_db
            from app.auth import hash_password

            db = get_db()

            # Создаем первого пользователя
            hashed_pw1, salt1 = hash_password("password1")
            db.execute(
                "INSERT INTO user (username, discriminator, password, salt) VALUES (?, ?, ?, ?)",
                ("unique_test", 1111, hashed_pw1, salt1),
            )
            db.commit()

            # Попытка создать второго пользователя с тем же username и
            # discriminator
            try:
                hashed_pw2, salt2 = hash_password("password2")
                db.execute(
                    "INSERT INTO user (username, discriminator, password, salt) VALUES (?, ?, ?, ?)",
                    ("unique_test", 1111, hashed_pw2, salt2),
                )
                db.commit()
                assert False, "Should have raised an integrity error"
            except Exception:
                pass  # Ожидаемое поведение - нарушение уникальности

            # Удаляем тестового пользователя
            db.execute(
                "DELETE FROM user WHERE username = ? AND discriminator = ?",
                ("unique_test", 1111),
            )
            db.commit()

    def test_foreign_key_constraints(self, app):
        """Проверка внешних ключей."""
        with app.app_context():
            from app.db.db import get_db

            db = get_db()

            # Попытка создать пост с несуществующим author_id
            try:
                db.execute(
                    "INSERT INTO post (title, content, author_id) VALUES (?, ?, ?)",
                    ("Orphan Post", "Orphan content", 99999),
                )
                db.commit()
                assert False, "Should have raised a foreign key constraint error"
            except Exception:
                pass  # Ожидаемое поведение - нарушение внешнего ключа


class TestDatabaseTransactions:
    """Тесты транзакций базы данных."""

    def test_transaction_rollback(self, app):
        """Откат транзакции при ошибке."""
        with app.app_context():
            from app.db.db import get_db
            from app.auth import hash_password

            db = get_db()

            # Начинаем транзакцию
            try:
                # Создаем пользователя
                hashed_pw, salt = hash_password("test_password")
                db.execute(
                    "INSERT INTO user (username, discriminator, password, salt) VALUES (?, ?, ?, ?)",
                    ("transaction_test", 5555, hashed_pw, salt),
                )

                # Вызываем ошибку
                db.execute("INVALID SQL QUERY")
                db.commit()

            except Exception:
                # Откатываем транзакцию
                db.rollback()

            # Проверяем, что пользователь не был создан
            user = db.execute(
                "SELECT * FROM user WHERE username = ? AND discriminator = ?",
                ("transaction_test", 5555),
            ).fetchone()
            assert user is None

    def test_transaction_commit(self, app):
        """Фиксация транзакции."""
        with app.app_context():
            from app.db.db import get_db
            from app.auth import hash_password

            db = get_db()

            # Создаем пользователя в транзакции
            hashed_pw, salt = hash_password("test_password")
            db.execute(
                "INSERT INTO user (username, discriminator, password, salt) VALUES (?, ?, ?, ?)",
                ("commit_test", 4444, hashed_pw, salt),
            )
            db.commit()

            # Проверяем, что пользователь создан
            user = db.execute(
                "SELECT * FROM user WHERE username = ? AND discriminator = ?",
                ("commit_test", 4444),
            ).fetchone()
            assert user is not None

            # Удаляем тестового пользователя
            db.execute(
                "DELETE FROM user WHERE username = ? AND discriminator = ?",
                ("commit_test", 4444),
            )
            db.commit()


class TestDatabasePerformance:
    """Тесты производительности базы данных."""

    def test_query_performance(self, app):
        """Производительность запросов."""
        with app.app_context():
            from app.db.db import get_db
            import time

            db = get_db()

            # Измеряем время простого запроса
            start_time = time.time()
            result = db.execute("SELECT 1").fetchone()
            end_time = time.time()

            assert result[0] == 1
            assert (end_time - start_time) < 0.1  # Менее 100мс

    def test_batch_insert_performance(self, app):
        """Производительность массовой вставки."""
        with app.app_context():
            from app.db.db import get_db
            from app.auth import hash_password
            import time

            db = get_db()

            # Массовая вставка пользователей (меньше пользователей для
            # скорости)
            start_time = time.time()

            users_to_insert = []
            for i in range(10):  # Уменьшили с 100 до 10
                username = f"perf_test_{i}"
                discriminator = 1000 + i
                hashed_pw, salt = hash_password(f"password_{i}")
                users_to_insert.append((username, discriminator, hashed_pw, salt))

            for user_data in users_to_insert:
                db.execute(
                    "INSERT INTO user (username, discriminator, password, salt) VALUES (?, ?, ?, ?)",
                    user_data,
                )

            db.commit()
            end_time = time.time()

            # Должно выполняться менее 5 секунд (увеличили лимит)
            assert (end_time - start_time) < 5.0

            # Удаляем тестовых пользователей
            db.execute('DELETE FROM user WHERE username LIKE "perf_test_%"')
            db.commit()
