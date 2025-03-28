from flask import Blueprint, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.comment import Comment
from app.forms.comment_form import CommentForm

bp = Blueprint('comments', __name__)

@bp.route('/article/<int:article_id>/comment', methods=['POST'])
@login_required
def manage_comments(article_id):
    form = CommentForm()
    if form.validate_on_submit():
        Comment.create(form.content.data, article_id, current_user.id)
        flash('Comment added successfully!', 'success')
    return redirect(url_for('articles.view_article', article_id=article_id))
