"""Blueprint для главных маршрутов приложения."""

from flask import Blueprint, render_template

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Главная страница блога."""
    return render_template('index.html')
