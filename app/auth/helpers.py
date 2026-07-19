"""Auth helpers: session cookie, decorators, identity helpers."""

from __future__ import annotations

import random
import re
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from flask import flash, g, redirect, session, url_for

from app.db import query_one

F = TypeVar("F", bound=Callable[..., Any])

RESERVED_USERNAME = "admin"
TAG_RE = re.compile(r"^([^#]+)#(\d{4})$")


def parse_tag(value: str) -> tuple[str, str] | None:
    """Parse name#0001 into (name, discriminator)."""
    match = TAG_RE.match(value.strip())
    if not match:
        return None
    return match.group(1), match.group(2)


def format_tag(name: str, discriminator: str) -> str:
    """Format Discord-style identity."""
    return f"{name}#{discriminator}"


def allocate_discriminator(name: str) -> str | None:
    """Pick a free 4-digit discriminator for name, or None if exhausted."""
    from app.db import query_all

    used = {
        row["discriminator"]
        for row in query_all(
            "SELECT discriminator FROM users WHERE name = ? COLLATE NOCASE",
            (name,),
        )
    }
    candidates = [f"{i:04d}" for i in range(1, 10000) if f"{i:04d}" not in used]
    if not candidates:
        return None
    return random.choice(candidates)


def load_logged_in_user() -> None:
    """Attach g.user from session user_id."""
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = query_one("SELECT * FROM users WHERE id = ?", (user_id,))
        if g.user is None:
            session.pop("user_id", None)


def login_user(user_id: int) -> None:
    """Store user id in the session cookie."""
    session.clear()
    session["user_id"] = user_id
    session.permanent = True


def logout_user() -> None:
    """Clear the session."""
    session.clear()
    g.user = None


def login_required(view: F) -> F:
    """Redirect anonymous users to login."""

    @wraps(view)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        if g.user is None:
            flash("Войдите, чтобы продолжить.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped  # type: ignore[return-value]


def admin_required(view: F) -> F:
    """Require authenticated admin."""

    @wraps(view)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        if g.user is None:
            flash("Войдите, чтобы продолжить.", "warning")
            return redirect(url_for("auth.login"))
        if not g.user["is_admin"]:
            flash("Недостаточно прав.", "danger")
            return redirect(url_for("posts.index"))
        return view(*args, **kwargs)

    return wrapped  # type: ignore[return-value]


def is_owner_or_admin(owner_id: int) -> bool:
    """True if current user owns the resource or is admin."""
    if g.user is None:
        return False
    return bool(g.user["is_admin"] or g.user["id"] == owner_id)
