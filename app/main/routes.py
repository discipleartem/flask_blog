"""Главные маршруты приложения."""

from flask import render_template

from app.main import bp


@bp.route('/')
def index():
    """Главная страница блога."""
    return render_template('index.html')
