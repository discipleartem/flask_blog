"""Comments blueprint: CRUD attached to posts."""

from __future__ import annotations

from flask import Blueprint, abort, flash, g, redirect, request, url_for

from app.auth.helpers import is_owner_or_admin, login_required
from app.db import execute, query_one

bp = Blueprint("comments", __name__)


@bp.route("/posts/<int:post_id>/comments", methods=("POST",))
@login_required
def create(post_id: int):
    """Add a comment to a post."""
    post = query_one("SELECT id FROM posts WHERE id = ?", (post_id,))
    if post is None:
        abort(404)
    body = (request.form.get("body") or "").strip()
    if not body:
        flash("Комментарий не может быть пустым.", "danger")
        return redirect(url_for("posts.detail", post_id=post_id))
    execute(
        "INSERT INTO comments (post_id, user_id, body) VALUES (?, ?, ?)",
        (post_id, g.user["id"], body),
    )
    flash("Комментарий добавлен.", "success")
    return redirect(url_for("posts.detail", post_id=post_id))


@bp.route("/comments/<int:comment_id>/edit", methods=("GET", "POST"))
@login_required
def edit(comment_id: int):
    """Edit own comment (or any as admin)."""
    from flask import render_template

    comment = query_one("SELECT * FROM comments WHERE id = ?", (comment_id,))
    if comment is None:
        abort(404)
    if not is_owner_or_admin(comment["user_id"]):
        abort(403)

    if request.method == "POST":
        body = (request.form.get("body") or "").strip()
        if not body:
            flash("Комментарий не может быть пустым.", "danger")
        else:
            execute(
                """
                UPDATE comments
                SET body = ?, updated_at = datetime('now')
                WHERE id = ?
                """,
                (body, comment_id),
            )
            flash("Комментарий обновлён.", "success")
            return redirect(url_for("posts.detail", post_id=comment["post_id"]))

    return render_template("comments/edit.html", comment=comment)


@bp.route("/comments/<int:comment_id>/delete", methods=("POST",))
@login_required
def delete(comment_id: int):
    """Delete own comment (or any as admin)."""
    comment = query_one("SELECT * FROM comments WHERE id = ?", (comment_id,))
    if comment is None:
        abort(404)
    if not is_owner_or_admin(comment["user_id"]):
        abort(403)
    post_id = comment["post_id"]
    execute("DELETE FROM comments WHERE id = ?", (comment_id,))
    flash("Комментарий удалён.", "info")
    return redirect(url_for("posts.detail", post_id=post_id))
