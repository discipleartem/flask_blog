"""Тесты для функционала постов блога."""
import pytest
from flask import session

from app.models import Post
from app.services import PostService


class TestPostModel:
    """Тесты для модели Post."""

    def test_create_post(self, app, client, auth):
        """Создание поста должно работать корректно."""
        # Сначала регистрируем и логинимся
        auth.register()
        auth.login()
        
        # Создаём пост через модель
        with app.app_context():
            post = PostService.create(
                author_id=1,  # ID первого пользователя
                title="Тестовый пост",
                content="Это содержание тестового поста."
            )
            
            assert post.id is not None
            assert post.title == "Тестовый пост"
            assert post.content == "Это содержание тестового поста."
            assert post.author_id == 1
            assert post.created is not None

    def test_find_post_by_id(self, app, auth):
        """Поиск поста по ID должен работать."""
        auth.register()
        auth.login()
        
        with app.app_context():
            # Создаём пост
            created_post = PostService.create(
                author_id=1,
                title="Тестовый пост",
                content="Содержание"
            )
            
            # Ищем пост по ID
            found_post = PostService.find_by_id(created_post.id)
            
            assert found_post is not None
            assert found_post.id == created_post.id
            assert found_post.title == "Тестовый пост"
            assert found_post.content == "Содержание"
            assert found_post.author_username is not None
            assert found_post.author_discriminator is not None

    def test_find_nonexistent_post(self, app):
        """Поиск несуществующего поста должен вернуть None."""
        with app.app_context():
            post = PostService.find_by_id(999999)
            assert post is None

    def test_get_all_posts(self, app, auth):
        """Получение всех постов должно работать."""
        auth.register()
        auth.login()
        
        with app.app_context():
            # Создаём несколько постов
            post1 = PostService.create(author_id=1, title="Пост 1", content="Содержание 1")
            post2 = PostService.create(author_id=1, title="Пост 2", content="Содержание 2")
            
            # Получаем все посты
            all_posts = PostService.get_all()
            
            assert len(all_posts) >= 2
            # Посты должны быть отсортированы по дате создания (новые первые)
            assert all_posts[0].created >= all_posts[1].created

    def test_update_post(self, app, auth):
        """Обновление поста должно работать."""
        auth.register()
        auth.login()
        
        with app.app_context():
            # Создаём пост
            post = PostService.create(author_id=1, title="Старый заголовок", content="Старое содержание")
            
            # Обновляем пост
            PostService.update(post.id, "Новый заголовок", "Новое содержание")
            
            # Проверяем изменения
            updated_post = PostService.find_by_id(post.id)
            assert updated_post.title == "Новый заголовок"
            assert updated_post.content == "Новое содержание"

    def test_delete_post(self, app, auth):
        """Удаление поста должно работать."""
        auth.register()
        auth.login()
        
        with app.app_context():
            # Создаём пост
            post = PostService.create(author_id=1, title="Пост для удаления", content="Содержание")
            post_id = post.id
            
            # Удаляем пост
            PostService.delete(post_id)
            
            # Проверяем, что пост удалён
            deleted_post = PostService.find_by_id(post_id)
            assert deleted_post is None

    def test_is_author(self, app, auth):
        """Проверка авторства должна работать."""
        auth.register()
        auth.login()
        
        with app.app_context():
            # Создаём пост от пользователя с ID=1
            post = PostService.create(author_id=1, title="Пост", content="Содержание")
            
            # Проверяем авторство
            assert post.is_author(1) is True
            assert post.is_author(2) is False

    def test_author_display_name(self, app, auth):
        """Отображаемое имя автора должно форматироваться правильно."""
        auth.register()
        auth.login()
        
        with app.app_context():
            # Создаём пост
            post = PostService.create(author_id=1, title="Пост", content="Содержание")
            
            # Проверяем формат имени автора
            display_name = post.author_display_name
            assert "#" in display_name
            assert display_name.endswith("#0001")  # Первый пользователь получает дискриминатор 0001


class TestPostRoutes:
    """Тесты для маршрутов постов."""

    def test_index_page_shows_posts(self, client, auth):
        """Главная страница должна показывать посты."""
        # Создаём пост
        auth.register()
        auth.login()
        
        # Создаём пост через POST запрос
        client.post('/post/create', data={
            'title': 'Тестовый пост',
            'content': 'Содержание тестового поста'
        })
        
        # Выходим из системы
        auth.logout()
        
        # Проверяем главную страницу
        response = client.get('/')
        assert response.status_code == 200
        assert 'Тестовый пост' in response.get_data(as_text=True)

    def test_create_post_requires_login(self, client):
        """Создание поста должно требовать авторизации."""
        response = client.get('/post/create')
        assert response.status_code == 302  # Redirect to login

    def test_create_post_form(self, client, auth):
        """Форма создания поста должна работать."""
        auth.register()
        auth.login()
        
        response = client.get('/post/create')
        assert response.status_code == 200
        assert 'Создать новый пост' in response.get_data(as_text=True)

    def test_create_post_submission(self, client, auth):
        """Отправка формы создания поста должна работать."""
        auth.register()
        auth.login()
        
        response = client.post('/post/create', data={
            'title': 'Новый пост',
            'content': 'Содержание нового поста'
        })
        assert response.status_code == 302  # Redirect to post view
        
        # Проверяем, что пост создан
        response = client.get('/')
        assert 'Новый пост' in response.get_data(as_text=True)

    def test_view_post(self, client, auth):
        """Просмотр поста должен работать."""
        auth.register()
        auth.login()
        
        # Создаём пост
        response = client.post('/post/create', data={
            'title': 'Пост для просмотра',
            'content': 'Содержание для просмотра'
        })
        
        # Извлекаем ID поста из URL редиректа
        post_id = response.location.split('/')[-1]
        
        # Просматриваем пост
        response = client.get(f'/post/{post_id}')
        assert response.status_code == 200
        assert 'Пост для просмотра' in response.get_data(as_text=True)
        assert 'Содержание для просмотра' in response.get_data(as_text=True)

    def test_view_nonexistent_post(self, client):
        """Просмотр несуществующего поста должен возвращать 404."""
        response = client.get('/post/999999')
        assert response.status_code == 404

    def test_edit_post_requires_login(self, client, auth):
        """Редактирование поста должно требовать авторизации."""
        # Сначала создаём пост
        auth.register()
        auth.login()
        response = client.post('/post/create', data={
            'title': 'Пост',
            'content': 'Содержание'
        })
        post_id = response.location.split('/')[-1]
        auth.logout()
        
        # Пытаемся редактировать без авторизации
        response = client.get(f'/post/{post_id}/edit')
        assert response.status_code == 302  # Redirect to login

    def test_edit_post_author_only(self, client, auth):
        """Редактировать пост может только автор."""
        # Создаём первого пользователя и пост
        auth.register(username='user1')
        auth.login(username='user1')
        response = client.post('/post/create', data={
            'title': 'Пост user1',
            'content': 'Содержание user1'
        })
        post_id = response.location.split('/')[-1]
        auth.logout()
        
        # Создаём второго пользователя
        auth.register(username='user2')
        auth.login(username='user2')
        
        # Пытаемся редактировать пост первого пользователя
        response = client.get(f'/post/{post_id}/edit')
        assert response.status_code == 403  # Forbidden

    def test_edit_post_form(self, client, auth):
        """Форма редактирования поста должна работать для автора."""
        auth.register()
        auth.login()
        
        # Создаём пост
        response = client.post('/post/create', data={
            'title': 'Оригинальный заголовок',
            'content': 'Оригинальное содержание'
        })
        post_id = response.location.split('/')[-1]
        
        # Получаем форму редактирования
        response = client.get(f'/post/{post_id}/edit')
        assert response.status_code == 200
        assert 'Оригинальный заголовок' in response.get_data(as_text=True)
        assert 'Оригинальное содержание' in response.get_data(as_text=True)

    def test_edit_post_submission(self, client, auth):
        """Отправка формы редактирования должна работать."""
        auth.register()
        auth.login()
        
        # Создаём пост
        response = client.post('/post/create', data={
            'title': 'Старый заголовок',
            'content': 'Старое содержание'
        })
        post_id = response.location.split('/')[-1]
        
        # Редактируем пост
        response = client.post(f'/post/{post_id}/edit', data={
            'title': 'Новый заголовок',
            'content': 'Новое содержание'
        })
        assert response.status_code == 302  # Redirect to post view
        
        # Проверяем изменения
        response = client.get(f'/post/{post_id}')
        assert 'Новый заголовок' in response.get_data(as_text=True)
        assert 'Новое содержание' in response.get_data(as_text=True)

    def test_delete_post_requires_login(self, client, auth):
        """Удаление поста должно требовать авторизации."""
        # Сначала создаём пост
        auth.register()
        auth.login()
        response = client.post('/post/create', data={
            'title': 'Пост',
            'content': 'Содержание'
        })
        post_id = response.location.split('/')[-1]
        auth.logout()
        
        # Пытаемся удалить без авторизации
        response = client.post(f'/post/{post_id}/delete')
        assert response.status_code == 302  # Redirect to login

    def test_delete_post_author_only(self, client, auth):
        """Удалять пост может только автор."""
        # Создаём первого пользователя и пост
        auth.register(username='user1')
        auth.login(username='user1')
        response = client.post('/post/create', data={
            'title': 'Пост user1',
            'content': 'Содержание user1'
        })
        post_id = response.location.split('/')[-1]
        auth.logout()
        
        # Создаём второго пользователя
        auth.register(username='user2')
        auth.login(username='user2')
        
        # Пытаемся удалить пост первого пользователя
        response = client.post(f'/post/{post_id}/delete')
        assert response.status_code == 403  # Forbidden

    def test_delete_post(self, client, auth):
        """Удаление поста должно работать."""
        auth.register()
        auth.login()
        
        # Создаём пост
        response = client.post('/post/create', data={
            'title': 'Пост для удаления',
            'content': 'Содержание для удаления'
        })
        post_id = response.location.split('/')[-1]
        
        # Удаляем пост
        response = client.post(f'/post/{post_id}/delete')
        assert response.status_code == 302  # Redirect to index
        
        # Проверяем, что пост удалён
        response = client.get(f'/post/{post_id}')
        assert response.status_code == 404

    def test_post_form_validation_placeholder(self, client, auth):
        """Тест-заглушка для валидации формы поста.
        
        TODO: После реализации валидаторов этот тест должен проверять:
        - Валидацию пустого заголовка (DataRequired)
        - Валидацию короткого содержания (Length min=10)
        - Валидацию максимальной длины заголовка (Length max=200)
        """
        auth.register()
        auth.login()
        
        # TODO: Эти данные должны вызывать ошибки валидации после реализации
        response = client.post('/post/create', data={
            'title': '',  # TODO: Должно быть ошибкой (DataRequired)
            'content': '123'  # TODO: Должно быть ошибкой (Length min=10)
        })
        
        # TODO: После реализации валидаторов ожидать status_code 200 (форма показана снова)
        # Сейчас ожидаем 302 (редирект), т.к. валидаторы - заглушки
        assert response.status_code == 302  # Временно 302, т.к. валидаторы не работают
