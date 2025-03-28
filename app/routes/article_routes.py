from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from werkzeug.exceptions import abort

from app.models.article import Article
from app.forms.article_forms import ArticleForm
from app.forms.comment_form import CommentForm
from app.models.comment import Comment

bp = Blueprint('articles', __name__)

@bp.route('/')
def index():
    return redirect(url_for('articles.list_articles'))

@bp.route('/articles')
def list_articles():
    articles = Article.get_all()
    return render_template('articles/list.html', articles=articles)

@bp.route('/article/<int:article_id>')
def view_article(article_id):
    article = Article.get_by_id(article_id)
    if article is None:
        abort(404)
    form = CommentForm()
    comments = Comment.get_by_article_id(article_id)
    return render_template('articles/view.html', article=article, comments=comments, form=form)

@bp.route('/article/new', methods=['GET', 'POST'])
@login_required
def new_article():
    form = ArticleForm()
    if form.validate_on_submit():
        Article.create(form.title.data, form.content.data, current_user.id)
        flash('Article created successfully!', 'success')
        return redirect(url_for('articles.list_articles'))
    return render_template('articles/form.html', form=form)


@bp.route('/article/<int:article_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_article(article_id):
    article = Article.get_by_id(article_id)
    if not article:
        flash('Article not found', 'danger')
        return redirect(url_for('articles.list_articles'))
    if article.user_id != current_user.id:
        flash('You are not authorized to edit this article', 'danger')
        return redirect(url_for('articles.list_articles'))

    form = ArticleForm(obj=article)
    if form.validate_on_submit():
        article.update_article(form.title.data, form.content.data)
        flash('Article updated successfully!', 'success')
        return redirect(url_for('articles.view_article', article_id=article.id))
    return render_template('articles/form.html', form=form, article=article)


@bp.route('/article/<int:article_id>/delete', methods=['POST'])
@login_required
def delete_article(article_id):
    article = Article.get_by_id(article_id)
    if article.user_id != current_user.id:
        flash('You are not authorized to delete this article', 'danger')
    else:
        article.delete()
        flash('Article deleted successfully!', 'success')
    return redirect(url_for('articles.list_articles'))