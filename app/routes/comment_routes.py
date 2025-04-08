from flask import Blueprint, redirect, url_for, flash, request, render_template
from flask_login import login_required, current_user
from app.models.comment import Comment
from app.forms.comment_form import CommentForm

bp = Blueprint('comments', __name__)

@bp.route('/article/<int:article_id>/comment', methods=['POST'])
@login_required
def create_comment(article_id):
    form = CommentForm()
    if form.validate_on_submit():
        Comment.create(form.content.data, article_id, current_user.id)
        flash('Comment added successfully!', 'success')
    return redirect(url_for('articles.view_article', article_id=article_id))


@bp.route('/article/<int:article_id>/comments/<int:comment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_comment(article_id, comment_id):
    comment = Comment.get_by_id(article_id, comment_id)

    if not comment or comment.user_id != current_user.id:
        flash('You do not have permission to edit this comment.', 'danger')
        return redirect(url_for('articles.view_article', article_id=article_id))

    form = CommentForm()

    if request.method == 'GET':
        # Перенаправляем на страницу статьи с идентификатором комментария для редактирования
        return redirect(url_for('articles.view_article',
                                article_id=article_id,
                                edit_comment_id=comment_id))

    if form.validate_on_submit():
        comment.update(form.content.data)
        flash('Comment updated successfully!', 'success')

    return redirect(url_for('articles.view_article', article_id=article_id))


@bp.route('/article/<int:article_id>/comments/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(article_id, comment_id):
    comment = Comment.get_by_id(article_id, comment_id)
    if comment and comment.user_id == current_user.id:
        comment.delete()
        flash('Comment deleted successfully!', 'success')
    else:
        flash('You do not have permission to delete this comment.', 'danger')
    return redirect(url_for('articles.view_article', article_id=article_id))