"""CSRF helpers for cookie-session forms."""

from __future__ import annotations

import secrets

from flask import request, session

CSRF_SESSION_KEY = "_csrf_token"
CSRF_FIELD = "csrf_token"
CSRF_HEADER = "X-CSRF-Token"


def ensure_csrf_token() -> str:
    """Return the session CSRF token, creating it if missing."""
    token = session.get(CSRF_SESSION_KEY)
    if not isinstance(token, str) or not token:
        token = secrets.token_urlsafe(32)
        session[CSRF_SESSION_KEY] = token
    return token


def validate_csrf() -> bool:
    """Validate CSRF token from form field or X-CSRF-Token header."""
    expected = session.get(CSRF_SESSION_KEY)
    if not isinstance(expected, str) or not expected:
        return False
    got = request.form.get(CSRF_FIELD) or request.headers.get(CSRF_HEADER)
    if not isinstance(got, str) or not got:
        return False
    return secrets.compare_digest(got, expected)
