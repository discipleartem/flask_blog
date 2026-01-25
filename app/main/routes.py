"""Главные маршруты приложения."""
from flask import Blueprint, render_template, request, flash, redirect, url_for, abort, g

from app.auth.utils import login_required
from app.services import PostService, CommentService
from app.models import Post
from app.forms import PostForm, CommentForm

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Главная страница блога - список всех постов."""
    posts = PostService.get_all()
    return render_template('main/index.html', posts=posts)


@bp.route('/post/create', methods=['GET', 'POST'])
@login_required
def create_post():
    """Создание нового поста."""
    form = PostForm(request.form)
    
    if request.method == 'POST' and form.validate():
        post = PostService.create(
            author_id=g.user['id'],
            title=form.title.data,
            content=form.content.data
        )
        flash('Пост успешно создан!', 'success')
        return redirect(url_for('main.view_post', post_id=post.id))
    
    # Если форма не валидна, показываем ошибки
    elif request.method == 'POST':
        for field_name, field_errors in form.errors.items():
            for error in field_errors:
                flash(error, 'danger')
    
    return render_template('main/create_post.html', form=form)


@bp.route('/post/<int:post_id>')
def view_post(post_id):
    """Просмотр отдельного поста."""
    post = PostService.find_by_id(post_id)
    if post is None:
        abort(404, description="Пост не найден")
    
    # Получаем комментарии к посту
    comments = CommentService.get_by_post_id(post_id)
    comment_form = CommentForm()
    
    return render_template('main/view_post.html', post=post, comments=comments, comment_form=comment_form)


@bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """Редактирование поста (только для автора)."""
    post = PostService.find_by_id(post_id)
    if post is None:
        abort(404, description="Пост не найден")
    
    if not post.is_author(g.user['id']):
        abort(403, description="Вы можете редактировать только свои посты")
    
    form = PostForm(request.form)
    
    if request.method == 'POST' and form.validate():
        PostService.update(post_id, form.title.data, form.content.data)
        flash('Пост успешно обновлён!', 'success')
        return redirect(url_for('main.view_post', post_id=post_id))
    elif request.method == 'GET':
        # Заполняем форму текущими данными поста
        form.title.data = post.title
        form.content.data = post.content
    
    # Если форма не валидна при POST, показываем ошибки
    elif request.method == 'POST':
        for field_name, field_errors in form.errors.items():
            for error in field_errors:
                flash(error, 'danger')
    
    return render_template('main/edit_post.html', form=form, post=post)


@bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """Удаление поста (только для автора)."""
    post = PostService.find_by_id(post_id)
    if post is None:
        abort(404, description="Пост не найден")
    
    if not post.is_author(g.user['id']):
        abort(403, description="Вы можете удалять только свои посты")
    
    # Проверяем CSRF токен
    form = PostForm(request.form)
    if not form.validate():
        for field_name, field_errors in form.errors.items():
            for error in field_errors:
                flash(error, 'danger')
        return redirect(url_for('main.view_post', post_id=post_id))
    
    PostService.delete(post_id)
    flash('Пост успешно удалён!', 'success')
    return redirect(url_for('main.index'))


@bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    """Добавление комментария к посту."""
    post = PostService.find_by_id(post_id)
    if post is None:
        abort(404, description="Пост не найден")
    
    form = CommentForm(request.form)
    
    if form.validate():
        comment = CommentService.create(
            author_id=g.user['id'],
            post_id=post_id,
            content=form.content.data
        )
        flash('Комментарий успешно добавлен!', 'success')
    else:
        # Показываем ошибки валидации
        for field_name, field_errors in form.errors.items():
            for error in field_errors:
                flash(error, 'danger')
    
    return redirect(url_for('main.view_post', post_id=post_id))


@bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    """Удаление комментария (только для автора)."""
    # Проверяем существование комментария
    comment = CommentService.find_by_id(comment_id)
    if comment is None:
        abort(404, description="Комментарий не найден")
    
    # Проверяем CSRF токен через пустую форму
    form = CommentForm(request.form)
    if not form.validate():
        for field_name, field_errors in form.errors.items():
            for error in field_errors:
                flash(error, 'danger')
        return redirect(url_for('main.view_post', post_id=comment.post_id))
    
    # Удаляем комментарий (проверка прав внутри сервиса)
    if CommentService.delete(comment_id, g.user['id']):
        flash('Комментарий успешно удалён!', 'success')
    else:
        flash('Вы можете удалять только свои комментарии', 'danger')
    
    return redirect(url_for('main.view_post', post_id=comment.post_id))
