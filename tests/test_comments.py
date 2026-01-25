"""Тесты для функционала комментариев."""
import pytest
from flask import session

from app.models import Comment
from app.services import CommentService


class TestCommentModel:
    """Тесты для модели Comment."""

    def test_create_comment(self, app, client, auth):
        """Создание комментария должно работать корректно."""
        # Сначала регистрируем, логинимся и создаём пост
        auth.register()
        auth.login()
        
        with app.app_context():
            # Создаём пост для комментария
            from app.services import PostService
            post = PostService.create(
                author_id=1,
                title="Тестовый пост",
                content="Содержание поста"
            )
            
            # Создаём комментарий
            comment = CommentService.create(
                author_id=1,
                post_id=post.id,
                content="Это тестовый комментарий"
            )
            
            assert comment.id is not None
            assert comment.content == "Это тестовый комментарий"
            assert comment.author_id == 1
            assert comment.post_id == post.id
            assert comment.created is not None
            assert comment.author_username is not None
            assert comment.author_discriminator is not None

    def test_find_comment_by_id(self, app, auth):
        """Поиск комментария по ID должен работать."""
        auth.register()
        auth.login()
        
        with app.app_context():
            # Создаём пост
            from app.services import PostService
            post = PostService.create(
                author_id=1,
                title="Тестовый пост",
                content="Содержание"
            )
            
            # Создаём комментарий
            created_comment = CommentService.create(
                author_id=1,
                post_id=post.id,
                content="Тестовый комментарий"
            )
            
            # Ищем комментарий по ID
            found_comment = CommentService.find_by_id(created_comment.id)
            
            assert found_comment is not None
            assert found_comment.id == created_comment.id
            assert found_comment.content == "Тестовый комментарий"

    def test_get_comments_by_post_id(self, app, auth):
        """Получение комментариев к посту должно работать."""
        auth.register()
        auth.login()
        
        with app.app_context():
            # Создаём пост
            from app.services import PostService
            post = PostService.create(
                author_id=1,
                title="Тестовый пост",
                content="Содержание"
            )
            
            # Создаём несколько комментариев
            comment1 = CommentService.create(
                author_id=1,
                post_id=post.id,
                content="Первый комментарий"
            )
            comment2 = CommentService.create(
                author_id=1,
                post_id=post.id,
                content="Второй комментарий"
            )
            
            # Получаем комментарии к посту
            comments = CommentService.get_by_post_id(post.id)
            
            assert len(comments) == 2
            assert comments[0].content in ["Первый комментарий", "Второй комментарий"]
            assert comments[1].content in ["Первый комментарий", "Второй комментарий"]

    def test_delete_own_comment(self, app, auth):
        """Удаление своего комментария должно работать."""
        auth.register()
        auth.login()
        
        with app.app_context():
            # Создаём пост
            from app.services import PostService
            post = PostService.create(
                author_id=1,
                title="Тестовый пост",
                content="Содержание"
            )
            
            # Создаём комментарий
            comment = CommentService.create(
                author_id=1,
                post_id=post.id,
                content="Тестовый комментарий"
            )
            
            # Удаляем свой комментарий
            result = CommentService.delete(comment.id, 1)
            
            assert result is True
            
            # Проверяем, что комментарий удалён
            deleted_comment = CommentService.find_by_id(comment.id)
            assert deleted_comment is None

    def test_delete_foreign_comment(self, app, auth):
        """Удаление чужого комментария не должно работать."""
        # Создаём двух пользователей
        auth.register(username="user1")
        auth.register(username="user2")
        
        with app.app_context():
            # Создаём пост от первого пользователя
            from app.services import PostService
            post = PostService.create(
                author_id=1,
                title="Тестовый пост",
                content="Содержание"
            )
            
            # Создаём комментарий от первого пользователя
            comment = CommentService.create(
                author_id=1,
                post_id=post.id,
                content="Комментарий пользователя 1"
            )
            
            # Пытаемся удалить комментарий от второго пользователя
            result = CommentService.delete(comment.id, 2)
            
            assert result is False
            
            # Проверяем, что комментарий не удалён
            existing_comment = CommentService.find_by_id(comment.id)
            assert existing_comment is not None

    def test_get_count_by_post_id(self, app, auth):
        """Подсчёт комментариев к посту должен работать."""
        auth.register()
        auth.login()
        
        with app.app_context():
            # Создаём пост
            from app.services import PostService
            post = PostService.create(
                author_id=1,
                title="Тестовый пост",
                content="Содержание"
            )
            
            # Проверяем количество комментариев (должно быть 0)
            count = CommentService.get_count_by_post_id(post.id)
            assert count == 0
            
            # Создаём несколько комментариев
            CommentService.create(
                author_id=1,
                post_id=post.id,
                content="Комментарий 1"
            )
            CommentService.create(
                author_id=1,
                post_id=post.id,
                content="Комментарий 2"
            )
            
            # Проверяем количество комментариев
            count = CommentService.get_count_by_post_id(post.id)
            assert count == 2


class TestCommentRoutes:
    """Тесты для маршрутов комментариев."""

    def test_add_comment_as_logged_in_user(self, client, auth):
        """Добавление комментария авторизованным пользователем."""
        auth.register()
        auth.login()
        
        # Создаём пост
        with client.application.app_context():
            from app.services import PostService
            post = PostService.create(
                author_id=1,
                title="Тестовый пост",
                content="Содержание поста"
            )
        
        # Добавляем комментарий
        with client.session_transaction() as sess:
            sess['csrf_token'] = 'test-csrf-token'
        
        response = client.post(
            f'/post/{post.id}/comment',
            data={
                'content': 'Новый комментарий',
                'csrf_token': 'test-csrf-token'
            },
            follow_redirects=True
        )
        
        assert response.status_code == 200
        # Проверяем, что комментарий появился в ответе
        content = response.data.decode('utf-8')
        assert 'Новый комментарий' in content

    def test_add_comment_as_anonymous_user(self, client, auth):
        """Добавление комментария анонимным пользователем должно быть запрещено."""
        # Создаём пост (нужно авторизоваться)
        auth.register()
        auth.login()
        
        with client.application.app_context():
            from app.services import PostService
            post = PostService.create(
                author_id=1,
                title="Тестовый пост",
                content="Содержание поста"
            )
        
        # Выходим из системы
        auth.logout()
        
        # Пытаемся добавить комментарий
        response = client.post(
            f'/post/{post.id}/comment',
            data={'content': 'Новый комментарий'},
            follow_redirects=True
        )
        
        # Должно перенаправить на страницу логина
        assert response.status_code == 200
        assert b'login' in response.data.lower()

    def test_delete_own_comment(self, client, auth):
        """Удаление своего комментария."""
        auth.register()
        auth.login()
        
        with client.application.app_context():
            # Создаём пост
            from app.services import PostService
            post = PostService.create(
                author_id=1,
                title="Тестовый пост",
                content="Содержание поста"
            )
            
            # Создаём комментарий
            comment = CommentService.create(
                author_id=1,
                post_id=post.id,
                content="Тестовый комментарий"
            )
        
        # Удаляем комментарий
        with client.session_transaction() as sess:
            sess['csrf_token'] = 'test-csrf-token'
        
        response = client.post(
            f'/comment/{comment.id}/delete',
            data={
                'csrf_token': 'test-csrf-token'
            },
            follow_redirects=True
        )
        
        assert response.status_code == 200
        # Проверяем, что комментарий удалён (его нет в ответе)
        content = response.data.decode('utf-8')
        assert 'Тестовый комментарий' not in content

    def test_view_post_with_comments(self, client, auth):
        """Просмотр поста с комментариями."""
        auth.register()
        auth.login()
        
        with client.application.app_context():
            # Создаём пост
            from app.services import PostService
            post = PostService.create(
                author_id=1,
                title="Тестовый пост",
                content="Содержание поста"
            )
            
            # Создаём комментарий
            CommentService.create(
                author_id=1,
                post_id=post.id,
                content="Тестовый комментарий"
            )
        
        # Просматриваем пост
        response = client.get(f'/post/{post.id}')
        
        assert response.status_code == 200
        # Проверяем наличие поста и секции комментариев
        content = response.data.decode('utf-8')
        assert 'Тестовый пост' in content
        assert 'Тестовый комментарий' in content
        # Проверяем наличие слова "Комментарии" в HTML
        assert 'Комментарии' in content


class TestCommentModelMethods:
    """Тесты для методов модели Comment."""

    def test_author_display_name(self):
        """Проверка отображаемого имени автора."""
        comment = Comment(
            author_username="testuser",
            author_discriminator=42
        )
        
        assert comment.author_display_name == "testuser#0042"

    def test_is_author(self):
        """Проверка метода is_author."""
        comment = Comment(author_id=123)
        
        assert comment.is_author(123) is True
        assert comment.is_author(456) is False

    def test_to_dict(self):
        """Проверка преобразования в словарь."""
        comment = Comment(
            id=1,
            author_id=123,
            post_id=456,
            content="Тест",
            author_username="user",
            author_discriminator=1
        )
        
        data = comment.to_dict()
        
        assert data['id'] == 1
        assert data['author_id'] == 123
        assert data['post_id'] == 456
        assert data['content'] == "Тест"
        assert data['author_display_name'] == "user#0001"

    def test_from_dict(self):
        """Проверка создания из словаря."""
        data = {
            'id': 1,
            'author_id': 123,
            'post_id': 456,
            'content': "Тест",
            'author_username': "user",
            'author_discriminator': 1
        }
        
        comment = Comment.from_dict(data)
        
        assert comment.id == 1
        assert comment.author_id == 123
        assert comment.post_id == 456
        assert comment.content == "Тест"
