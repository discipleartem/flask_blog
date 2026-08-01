"""Модуль PythonAnywhere: настройки из Админки и read-only API-клиент.

Учётные данные задаются только формами в `/admin/modules/pythonanywhere`.
Не читать `PA_*` / `API_TOKEN` из env или GitHub Secrets.
"""

from __future__ import annotations

import json
import ssl
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.db import execute, query_one

_ALLOWED_HOSTS = frozenset(
    {
        "www.pythonanywhere.com",
        "eu.pythonanywhere.com",
    }
)
ALLOWED_HOSTS = _ALLOWED_HOSTS


@dataclass(frozen=True)
class PaSettings:
    """Настройки модуля PA (singleton)."""

    enabled: bool
    api_token: str
    username: str
    api_host: str
    webapp_domain: str
    monitor_cpu: bool
    monitor_webapps: bool
    monitor_schedule: bool
    monitor_always_on: bool
    monitor_consoles: bool
    updated_at: str | None = None

    @property
    def has_credentials(self) -> bool:
        """True, если можно вызывать API."""
        return bool(self.api_token.strip() and self.username.strip())

    @property
    def token_configured(self) -> bool:
        """Токен сохранён (для маски в форме)."""
        return bool(self.api_token.strip())


@dataclass(frozen=True)
class PaApiResult:
    """Ответ одного GET к PA API."""

    ok: bool
    status_code: int | None
    data: Any = None
    error: str | None = None


def get_settings() -> PaSettings:
    """Загрузить singleton-настройки модуля."""
    row = query_one("SELECT * FROM pa_module_settings WHERE id = 1")
    if row is None:
        execute("INSERT OR IGNORE INTO pa_module_settings (id) VALUES (1)")
        row = query_one("SELECT * FROM pa_module_settings WHERE id = 1")
    assert row is not None
    return PaSettings(
        enabled=bool(row["enabled"]),
        api_token=row["api_token"] or "",
        username=(row["username"] or "").strip(),
        api_host=(row["api_host"] or "www.pythonanywhere.com").strip(),
        webapp_domain=(row["webapp_domain"] or "").strip(),
        monitor_cpu=bool(row["monitor_cpu"]),
        monitor_webapps=bool(row["monitor_webapps"]),
        monitor_schedule=bool(row["monitor_schedule"]),
        monitor_always_on=bool(row["monitor_always_on"]),
        monitor_consoles=bool(row["monitor_consoles"]),
        updated_at=row["updated_at"],
    )


def save_settings(
    *,
    enabled: bool,
    username: str,
    api_host: str,
    webapp_domain: str,
    api_token: str | None,
    keep_existing_token: bool,
    monitor_cpu: bool,
    monitor_webapps: bool,
    monitor_schedule: bool,
    monitor_always_on: bool,
    monitor_consoles: bool,
) -> str | None:
    """Сохранить настройки из формы. Возвращает текст ошибки или None.

    ``api_token``: новое значение; если пусто и ``keep_existing_token`` —
    токен не меняется. Пустой токен при сбросе допускается только явно
    (поле cleared + keep False).
    """
    host = api_host.strip()
    if host not in _ALLOWED_HOSTS:
        return "Недопустимый API host. Выберите www или eu."

    current = get_settings()
    token = current.api_token
    if api_token is not None and api_token.strip():
        token = api_token.strip()
    elif not keep_existing_token:
        token = ""

    execute(
        """
        UPDATE pa_module_settings
        SET enabled = ?,
            api_token = ?,
            username = ?,
            api_host = ?,
            webapp_domain = ?,
            monitor_cpu = ?,
            monitor_webapps = ?,
            monitor_schedule = ?,
            monitor_always_on = ?,
            monitor_consoles = ?,
            updated_at = datetime('now')
        WHERE id = 1
        """,
        (
            1 if enabled else 0,
            token,
            username.strip(),
            host,
            webapp_domain.strip(),
            1 if monitor_cpu else 0,
            1 if monitor_webapps else 0,
            1 if monitor_schedule else 0,
            1 if monitor_always_on else 0,
            1 if monitor_consoles else 0,
        ),
    )
    return None


def _api_get(settings: PaSettings, path: str) -> PaApiResult:
    """GET https://{host}/api/v0/user/{username}/{path}."""
    if not settings.has_credentials:
        return PaApiResult(ok=False, status_code=None, error="Нет username/token")
    if settings.api_host not in _ALLOWED_HOSTS:
        return PaApiResult(ok=False, status_code=None, error="Недопустимый host")

    base = f"https://{settings.api_host}/api/v0/user/{settings.username}"
    url = f"{base}/{path.lstrip('/')}"
    req = Request(
        url,
        headers={"Authorization": f"Token {settings.api_token}"},
        method="GET",
    )
    try:
        with urlopen(req, timeout=12, context=ssl.create_default_context()) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            status = getattr(resp, "status", 200)
            try:
                data = json.loads(raw) if raw else None
            except json.JSONDecodeError:
                return PaApiResult(
                    ok=False,
                    status_code=status,
                    error="Ответ не JSON",
                )
            return PaApiResult(ok=True, status_code=status, data=data)
    except HTTPError as exc:
        body = ""
        try:
            body = exc.read().decode("utf-8", errors="replace")[:200]
        except Exception:  # noqa: BLE001
            pass
        return PaApiResult(
            ok=False,
            status_code=exc.code,
            error=f"HTTP {exc.code}" + (f": {body}" if body else ""),
        )
    except URLError as exc:
        return PaApiResult(ok=False, status_code=None, error=str(exc.reason))
    except TimeoutError:
        return PaApiResult(ok=False, status_code=None, error="Timeout")


def fetch_monitoring(settings: PaSettings | None = None) -> dict[str, Any]:
    """Собрать блоки мониторинга по включённым чекбоксам.

    Returns:
        Словарь для шаблона: enabled, configured, blocks[{key, title, result}].
    """
    settings = settings or get_settings()
    out: dict[str, Any] = {
        "enabled": settings.enabled,
        "configured": settings.has_credentials,
        "username": settings.username,
        "api_host": settings.api_host,
        "webapp_domain": settings.webapp_domain,
        "blocks": [],
    }
    if not settings.enabled:
        return out
    if not settings.has_credentials:
        return out

    specs: list[tuple[str, str, str, bool]] = [
        ("cpu", "CPU", "cpu/", settings.monitor_cpu),
        ("webapps", "Webapps", "webapps/", settings.monitor_webapps),
        ("schedule", "Schedule", "schedule/", settings.monitor_schedule),
        ("always_on", "Always-on", "always_on/", settings.monitor_always_on),
        ("consoles", "Consoles", "consoles/", settings.monitor_consoles),
    ]
    for key, title, path, on in specs:
        if not on:
            continue
        result = _api_get(settings, path)
        out["blocks"].append(
            {
                "key": key,
                "title": title,
                "result": result,
            }
        )
    return out


def settings_from_form(form: Any) -> tuple[dict[str, Any], str | None]:
    """Разобрать POST-форму модуля → kwargs для save_settings + ошибка."""
    api_host = (form.get("api_host") or "").strip()
    username = (form.get("username") or "").strip()
    webapp_domain = (form.get("webapp_domain") or "").strip()
    token_new = (form.get("api_token") or "").strip()
    clear_token = form.get("clear_token") == "on"
    enabled = form.get("enabled") == "on"

    if enabled and not username:
        return {}, "Укажите username PythonAnywhere."
    if enabled and api_host not in _ALLOWED_HOSTS:
        return {}, "Выберите API host (www или eu)."

    current = get_settings()
    if clear_token:
        keep = False
        token_value: str | None = None
    elif token_new:
        keep = False
        token_value = token_new
    else:
        keep = True
        token_value = None

    will_have_token = bool(token_value) if not keep else current.token_configured
    if clear_token:
        will_have_token = False
    if enabled and not will_have_token:
        return {}, "Для включения модуля нужен API token."

    return {
        "enabled": enabled,
        "username": username,
        "api_host": api_host or "www.pythonanywhere.com",
        "webapp_domain": webapp_domain,
        "api_token": token_value,
        "keep_existing_token": keep,
        "monitor_cpu": form.get("monitor_cpu") == "on",
        "monitor_webapps": form.get("monitor_webapps") == "on",
        "monitor_schedule": form.get("monitor_schedule") == "on",
        "monitor_always_on": form.get("monitor_always_on") == "on",
        "monitor_consoles": form.get("monitor_consoles") == "on",
    }, None
