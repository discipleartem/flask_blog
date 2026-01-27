"""Blueprint авторизации."""

from flask import Blueprint

bp = Blueprint("auth", __name__, url_prefix="/auth")

__all__ = ["bp"]

from app.auth import routes  # noqa: E402, F401
from app.auth.utils import (
    hash_password,
    verify_password,
    generate_discriminator,
    login_required,
)  # noqa: E402, F401
