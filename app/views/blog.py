"""Blueprint для блог-функциональности.

Применяемые паттерны:
- Controller — обработка HTTP запросов блога
- Blueprint — организация маршрутов блога
- Pagination — постраничная навигация

Применяемые принципы:
- Single Responsibility — только блог-функциональность
- Explicit is better than implicit — явные ответы
- Fail fast — ранние проверки и ошибки
"""

from flask import Blueprint, current_app, redirect, render_template, request, url_for

from ..auth import get_current_user, is_authenticated, login_required

blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/')
def index():
    """Главная страница с постами, сгруппированными по пользователям."""
    posts = current_app.post_service.get_posts_grouped_by_users(limit_per_user=3)
    return render_template('blog/index.html', posts=posts)


@blog_bp.route('/posts')
def posts():
    """Страница со всеми постами с пагинацией."""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    posts, total = current_app.post_service.get_all_posts(page=page, per_page=per_page)
    
    # Рассчитываем пагинацию
    total_pages = (total + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    
    return render_template('blog/posts.html', 
                         posts=posts,
                         page=page,
                         per_page=per_page,
                         total=total,
                         total_pages=total_pages,
                         has_prev=has_prev,
                         has_next=has_next)


@blog_bp.route('/post/<int:post_id>')
def view_post(post_id):
    """Просмотр отдельного поста с комментариями."""
    post = current_app.post_service.get_post_by_id(post_id)
    
    if not post:
        return render_template('errors/404.html'), 404
    
    comments = current_app.comment_service.get_post_comments(post_id)
    comments_count = current_app.comment_service.get_post_comments_count(post_id)
    
    return render_template('blog/post_detail.html', 
                         post=post,
                         comments=comments,
                         comments_count=comments_count)


@blog_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    """Создание нового поста."""
    if request.method == 'GET':
        return render_template('blog/create_post.html')
    
    # POST запрос
    title = request.form.get('title', '').strip()
    body = request.form.get('body', '').strip()
    
    success, message, post = current_app.post_service.create_post(
        user_id=get_current_user().id,
        title=title,
        body=body
    )
    
    if success and post:
        return redirect(url_for('blog.view_post', post_id=post.id))
    else:
        return render_template('blog/create_post.html', 
                             title=title,
                             body=body,
                             error=message)


@blog_bp.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """Редактирование поста."""
    post = current_app.post_service.get_post_by_id(post_id)
    
    if not post:
        return render_template('errors/404.html'), 404
    
    # Проверяем права на редактирование
    current_user = get_current_user()
    if not current_app.post_service.can_user_edit_post(post_id, current_user.id, current_user.is_admin):
        return render_template('errors/403.html'), 403
    
    if request.method == 'GET':
        return render_template('blog/edit_post.html', post=post)
    
    # POST запрос
    title = request.form.get('title', '').strip()
    body = request.form.get('body', '').strip()
    
    success, message, updated_post = current_app.post_service.update_post(
        post_id=post_id,
        user_id=current_user.id,
        title=title,
        body=body,
        is_admin=current_user.is_admin
    )
    
    if success and updated_post:
        return redirect(url_for('blog.view_post', post_id=updated_post.id))
    else:
        return render_template('blog/edit_post.html', 
                             post=post,
                             title=title,
                             body=body,
                             error=message)


@blog_bp.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    """Удаление поста."""
    post = current_app.post_service.get_post_by_id(post_id)
    
    if not post:
        return render_template('errors/404.html'), 404
    
    # Проверяем права на удаление
    current_user = get_current_user()
    if not current_app.post_service.can_user_delete_post(post_id, current_user.id, current_user.is_admin):
        return render_template('errors/403.html'), 403
    
    success, message = current_app.post_service.delete_post(
        post_id=post_id,
        user_id=current_user.id,
        is_admin=current_user.is_admin
    )
    
    if success:
        return redirect(url_for('blog.index'))
    else:
        # В случае ошибки, возвращаемся на страницу поста
        return redirect(url_for('blog.view_post', post_id=post_id))


@blog_bp.route('/comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    """Добавление комментария к посту."""
    post = current_app.post_service.get_post_by_id(post_id)
    
    if not post:
        return render_template('errors/404.html'), 404
    
    body = request.form.get('body', '').strip()
    
    success, message, comment = current_app.comment_service.create_comment(
        post_id=post_id,
        user_id=get_current_user().id,
        body=body
    )
    
    if success and comment:
        return redirect(url_for('blog.view_post', post_id=post_id))
    else:
        # В случае ошибки, возвращаемся на страницу поста с сообщением
        comments = current_app.comment_service.get_post_comments(post_id)
        comments_count = current_app.comment_service.get_post_comments_count(post_id)
        
        return render_template('blog/post_detail.html', 
                             post=post,
                             comments=comments,
                             comments_count=comments_count,
                             comment_body=body,
                             comment_error=message)


@blog_bp.route('/comment/edit/<int:comment_id>', methods=['GET', 'POST'])
@login_required
def edit_comment(comment_id):
    """Редактирование комментария."""
    comment = current_app.comment_service.get_comment_by_id(comment_id)
    
    if not comment:
        return render_template('errors/404.html'), 404
    
    # Проверяем права на редактирование
    current_user = get_current_user()
    if not current_app.comment_service.can_user_edit_comment(comment_id, current_user.id, current_user.is_admin):
        return render_template('errors/403.html'), 403
    
    if request.method == 'GET':
        return render_template('blog/edit_comment.html', comment=comment)
    
    # POST запрос
    body = request.form.get('body', '').strip()
    
    success, message, updated_comment = current_app.comment_service.update_comment(
        comment_id=comment_id,
        user_id=current_user.id,
        body=body,
        is_admin=current_user.is_admin
    )
    
    if success and updated_comment:
        return redirect(url_for('blog.view_post', post_id=updated_comment.post_id))
    else:
        return render_template('blog/edit_comment.html', 
                             comment=comment,
                             body=body,
                             error=message)


@blog_bp.route('/comment/delete/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    """Удаление комментария."""
    comment = current_app.comment_service.get_comment_by_id(comment_id)
    
    if not comment:
        return render_template('errors/404.html'), 404
    
    # Проверяем права на удаление
    current_user = get_current_user()
    if not current_app.comment_service.can_user_delete_comment(comment_id, current_user.id, current_user.is_admin):
        return render_template('errors/403.html'), 403
    
    success, message = current_app.comment_service.delete_comment(
        comment_id=comment_id,
        user_id=current_user.id,
        is_admin=current_user.is_admin
    )
    
    # Всегда возвращаемся на страницу поста
    return redirect(url_for('blog.view_post', post_id=comment.post_id))