"""Blueprint для главных маршрутов приложения."""

from flask import Blueprint, render_template

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Главная страница блога.
    
    Отображает приветственную страницу с информацией о текущем пользователе,
    если он авторизован.
    """
    return render_template('index.html')
