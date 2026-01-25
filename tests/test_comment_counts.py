"""Тесты для проверки счетчиков комментариев на главной странице."""
import pytest
from app.services.post_service import PostService
from app.services.comment_service import CommentService


class TestCommentCounts:
    """Тестирование счетчиков комментариев."""
    
    def test_post_service_get_all_includes_comment_count(self, app):
        """Проверяет, что PostService.get_all() возвращает посты с количеством комментариев."""
        with app.app_context():
            posts = PostService.get_all()
            
            # Проверяем, что у всех постов есть поле comment_count
            for post in posts:
                assert hasattr(post, 'comment_count'), f"У поста {post.id} нет поля comment_count"
                assert isinstance(post.comment_count, int), f"comment_count должен быть int, а не {type(post.comment_count)}"
                assert post.comment_count >= 0, f"comment_count не может быть отрицательным: {post.comment_count}"
    
    def test_comment_count_matches_database(self, app):
        """Проверяет, что счетчики комментариев соответствуют данным в БД."""
        with app.app_context():
            posts = PostService.get_all()
            
            for post in posts:
                # Получаем количество комментариев напрямую из БД
                actual_count = CommentService.get_count_by_post_id(post.id)
                
                # Сравниваем со значением из PostService
                assert post.comment_count == actual_count, (
                    f"Несоответствие для поста {post.id}: "
                    f"PostService вернул {post.comment_count}, "
                    f"в БД фактически {actual_count}"
                )
    
    def test_index_page_renders_comment_counts(self, client):
        """Проверяет, что главная страница корректно отображает счетчики комментариев."""
        response = client.get('/')
        assert response.status_code == 200
        
        html = response.get_data(as_text=True)
        
        # Получаем посты для проверки
        with client.application.app_context():
            posts = PostService.get_all()
            
            # Проверяем, что каждый пост отображает правильное количество комментариев
            for post in posts:
                # Ищем в HTML количество комментариев для этого поста
                import re
                # Ищем ссылку на пост и следующий за ней блок с комментариями
                post_pattern = f'href="/post/{post.id}"[^>]*>.*?fa-comment[^>]*>.*?<span[^>]*>(\d+)</span>'
                matches = re.findall(post_pattern, html, re.DOTALL)
                
                if matches:
                    displayed_count = int(matches[0])
                    assert displayed_count == post.comment_count, (
                        f"Для поста {post.id} отображается {displayed_count}, "
                        f"а должно быть {post.comment_count}"
                    )
    
    def test_comment_count_zero_for_posts_without_comments(self, app):
        """Проверяет, что у постов без комментариев счетчик равен 0."""
        with app.app_context():
            posts = PostService.get_all()
            
            for post in posts:
                actual_count = CommentService.get_count_by_post_id(post.id)
                if actual_count == 0:
                    assert post.comment_count == 0, f"У поста {post.id} без комментариев счетчик должен быть 0"
    
    def test_comment_count_positive_for_posts_with_comments(self, app):
        """Проверяет, что у постов с комментариями счетчик больше 0."""
        with app.app_context():
            posts = PostService.get_all()
            
            for post in posts:
                actual_count = CommentService.get_count_by_post_id(post.id)
                if actual_count > 0:
                    assert post.comment_count > 0, f"У поста {post.id} с комментариями счетчик должен быть > 0"
                    assert post.comment_count == actual_count, (
                        f"У поста {post.id} счетчик {post.comment_count}, "
                        f"а в БД {actual_count}"
                    )
