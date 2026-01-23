"""Главные маршруты приложения."""
from flask import Blueprint, render_template, request, flash, redirect, url_for, abort, g

from app.auth.utils import login_required
from app.db import Post
from app.forms import PostForm

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Главная страница блога - список всех постов."""
    posts = Post.get_all()
    return render_template('main/index.html', posts=posts)


@bp.route('/post/create', methods=['GET', 'POST'])
@login_required
def create_post():
    """Создание нового поста."""
    form = PostForm(request.form)
    
    if request.method == 'POST' and form.validate():
        post = Post.create(
            author_id=g.user['id'],
            title=form.title.data,
            content=form.content.data
        )
        flash('Пост успешно создан!', 'success')
        return redirect(url_for('main.view_post', post_id=post.id))
    
    return render_template('main/create_post.html', form=form)


@bp.route('/post/<int:post_id>')
def view_post(post_id):
    """Просмотр отдельного поста."""
    post = Post.find_by_id(post_id)
    if post is None:
        abort(404, description="Пост не найден")
    
    return render_template('main/view_post.html', post=post)


@bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """Редактирование поста (только для автора)."""
    post = Post.find_by_id(post_id)
    if post is None:
        abort(404, description="Пост не найден")
    
    if not post.is_author(g.user['id']):
        abort(403, description="Вы можете редактировать только свои посты")
    
    form = PostForm(request.form)
    
    if request.method == 'POST' and form.validate():
        post.update(form.title.data, form.content.data)
        flash('Пост успешно обновлён!', 'success')
        return redirect(url_for('main.view_post', post_id=post.id))
    elif request.method == 'GET':
        # Заполняем форму текущими данными поста
        form.title.data = post.title
        form.content.data = post.content
    
    return render_template('main/edit_post.html', form=form, post=post)


@bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """Удаление поста (только для автора)."""
    post = Post.find_by_id(post_id)
    if post is None:
        abort(404, description="Пост не найден")
    
    if not post.is_author(g.user['id']):
        abort(403, description="Вы можете удалять только свои посты")
    
    post.delete()
    flash('Пост успешно удалён!', 'success')
    return redirect(url_for('main.index'))
