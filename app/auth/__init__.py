"""Blueprint авторизации."""

from flask import Blueprint

bp = Blueprint('auth', __name__, url_prefix='/auth')

from app.auth.utils import hash_password, verify_password, generate_discriminator

from app.auth import routes  # noqa: E402, F401
