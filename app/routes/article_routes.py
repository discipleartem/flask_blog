from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.exceptions import abort

from app.models.article import Article
from app.forms.article_forms import ArticleForm
from app.forms.comment_form import CommentForm
from app.models.comment import Comment

# Создаем Blueprint для маршрутов, связанных со статьями
bp = Blueprint('articles', __name__)

@bp.route('/')
def index():
    """Перенаправление с корневого маршрута на список статей"""
    return redirect(url_for('articles.list_articles'))

@bp.route('/articles')
def list_articles():
    """Отображение списка всех статей"""
    articles = Article.get_all()
    return render_template('articles/list.html', articles=articles)



@bp.route('/article/<int:article_id>', methods=['GET'])
def view_article(article_id):
    article = Article.get_by_id(article_id)
    if not article:
        flash('Article not found.', 'danger')
        return redirect(url_for('articles.list_articles'))

    comments = Comment.get_by_article_id(article_id)
    new_comment_form = CommentForm()  # Форма для нового комментария
    edit_comment_form = None  # По умолчанию форма редактирования не нужна


    # Если есть параметр edit_comment_id, значит пользователь хочет редактировать комментарий
    edit_comment_id = request.args.get('edit_comment_id')
    if edit_comment_id and current_user.is_authenticated:
        edit_comment = Comment.get_by_id(article_id, int(edit_comment_id))
        if edit_comment and edit_comment.user_id == current_user.id:
            edit_comment_form = CommentForm()
            edit_comment_form.content.data = edit_comment.content

    return render_template('articles/view.html',
                           article=article,
                           comments=comments,
                           new_comment_form=new_comment_form,
                           edit_comment_form=edit_comment_form)



@bp.route('/article/new', methods=['GET', 'POST'])
@login_required  # Требуется аутентификация для создания статьи
def new_article():
    """Создание новой статьи"""
    form = ArticleForm()
    if form.validate_on_submit():
        Article.create(form.title.data, form.content.data, current_user.id)
        flash('Article created successfully!', 'success')
        return redirect(url_for('articles.list_articles'))
    return render_template('articles/form.html', form=form)



@bp.route('/article/<int:article_id>/edit', methods=['GET', 'POST'])
@login_required  # Требуется аутентификация для редактирования
def edit_article(article_id):
    """
    Редактирование существующей статьи.
    Проверяет права доступа перед редактированием
    """
    article = Article.get_by_id(article_id)
    if not article:
        flash('Article not found', 'danger')
        return redirect(url_for('articles.list_articles'))
    if article.user_id != current_user.id:
        flash('You are not authorized to edit this article', 'danger')
        return redirect(url_for('articles.list_articles'))

    form = ArticleForm(obj=article)
    if form.validate_on_submit():
        article.update(form.title.data, form.content.data)
        flash('Article updated successfully!', 'success')
        return redirect(url_for('articles.view_article', article_id=article.id))
    return render_template('articles/form.html', form=form, article=article)



@bp.route('/article/<int:article_id>/delete', methods=['POST'])
@login_required  # Требуется аутентификация для удаления
def delete_article(article_id):
    """
    Удаление статьи.
    Проверяет права доступа перед удалением
    """
    article = Article.get_by_id(article_id)
    if article.user_id != current_user.id:
        flash('You are not authorized to delete this article', 'danger')
    else:
        article.delete()
        flash('Article deleted successfully!', 'success')
    return redirect(url_for('articles.list_articles'))