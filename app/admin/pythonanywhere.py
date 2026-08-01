"""Модуль PythonAnywhere: настройки из Админки и read-only API-клиент.

Учётные данные задаются только формами в `/admin/modules/pythonanywhere`.
Не читать `PA_*` / `API_TOKEN` из env или GitHub Secrets.
"""

from __future__ import annotations

import json
import os
import ssl
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.config import Config
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
    monitor_disk: bool
    disk_quota_mib: int
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
        monitor_disk=bool(row["monitor_disk"]) if "monitor_disk" in row.keys() else False,
        disk_quota_mib=_disk_quota_from_row(row),
        updated_at=row["updated_at"],
    )


def _disk_quota_from_row(row: Any) -> int:
    """Лимит диска из БД; пустое/битое → Config.PA_DISC_FREE."""
    if "disk_quota_mib" not in row.keys():
        return Config.PA_DISC_FREE
    raw = row["disk_quota_mib"]
    if raw is None or raw == "":
        return Config.PA_DISC_FREE
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return Config.PA_DISC_FREE
    return value if value >= 1 else Config.PA_DISC_FREE



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
    monitor_disk: bool,
    disk_quota_mib: int,
) -> str | None:
    """Сохранить настройки из формы. Возвращает текст ошибки или None.

    ``api_token``: новое значение; если пусто и ``keep_existing_token`` —
    токен не меняется. Пустой токен при сбросе допускается только явно
    (поле cleared + keep False).
    """
    host = api_host.strip()
    if host not in _ALLOWED_HOSTS:
        return "Недопустимый API host. Выберите www или eu."
    if disk_quota_mib < 1:
        return "Квота диска должна быть не меньше 1 МиБ."

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
            monitor_disk = ?,
            disk_quota_mib = ?,
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
            1 if monitor_disk else 0,
            int(disk_quota_mib),
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
        ("cpu", "Дневная квота CPU", "cpu/", settings.monitor_cpu),
        ("disk", "Жёсткий диск", "", settings.monitor_disk),
        ("webapps", "Веб-приложения", "webapps/", settings.monitor_webapps),
        ("schedule", "Расписание задач", "schedule/", settings.monitor_schedule),
        ("always_on", "Always-on задачи", "always_on/", settings.monitor_always_on),
        ("consoles", "Консоли", "consoles/", settings.monitor_consoles),
    ]
    for key, title, path, on in specs:
        if not on:
            continue
        if key == "disk":
            result, view = _fetch_disk(settings)
            out["blocks"].append(
                {
                    "key": key,
                    "title": title,
                    "result": result,
                    "view": view,
                }
            )
            continue
        result = _api_get(settings, path)
        block: dict[str, Any] = {
            "key": key,
            "title": title,
            "result": result,
            "view": None,
        }
        if result.ok:
            block["view"] = _friendly_view(key, result.data)
        out["blocks"].append(block)
    return out


def _format_reset(value: Any) -> str:
    """ISO-время сброса → дд.мм.гггг чч:мм UTC."""
    if value is None or value == "":
        return "—"
    text = str(value).strip()
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return dt.strftime("%d.%m.%Y %H:%M UTC")
    except ValueError:
        return text


def _cpu_view(data: dict[str, Any]) -> dict[str, Any]:
    """Человекочитаемая сводка дневной квоты CPU (секунды процессора)."""
    used = data.get("daily_cpu_total_usage_seconds")
    limit = data.get("daily_cpu_limit_seconds")
    percent: float | None = None
    try:
        used_f = float(used) if used is not None else None
        limit_f = float(limit) if limit is not None else None
    except (TypeError, ValueError):
        used_f, limit_f = None, None
    if used_f is not None and limit_f and limit_f > 0:
        percent = round(100.0 * used_f / limit_f, 1)
    bar = 0.0 if percent is None else min(100.0, max(0.0, percent))
    return {
        "kind": "cpu",
        "used": used_f,
        "limit": limit_f,
        "percent": percent,
        "bar": bar,
        "reset": _format_reset(data.get("next_reset_time")),
        "hint": (
            "Секунды работы процессора за сутки на тарифе PythonAnywhere "
            "(не процент загрузки сервера)."
        ),
    }


def _format_mib(value: float | None) -> str:
    """МиБ с одним знаком после запятой (или целые, если почти целые)."""
    if value is None:
        return "—"
    if abs(value - round(value)) < 0.05:
        return f"{int(round(value))} МиБ"
    return f"{value:.1f} МиБ"


def _home_disk_usage_bytes(username: str) -> tuple[int | None, str | None]:
    """Занятость диска по формуле PA Disk Quota (du + awk).

    Официально:
    https://help.pythonanywhere.com/pages/DiskQuota
    ``du -s -B 1 /tmp ~/.[!.]* ~/* | awk '{s+=$1}END{print s}'``

    None — не на хосте PA / ошибка измерения.
    """
    home = Path(f"/home/{username}")
    if not home.is_dir():
        return None, (
            "Каталог домашнего аккаунта недоступен на этой машине. "
            "Занятость считается по формуле PA Disk Quota только когда "
            "приложение запущено на PythonAnywhere. "
            "Квоту смотрите в Dashboard → Files на PA."
        )
    # bash + те же пути, что в справке PA; HOME фиксируем на username.
    script = (
        'du -s -B 1 /tmp "$HOME"/.[!.]* "$HOME"/* 2>/dev/null '
        "| awk '{s+=$1}END{print s+0}'"
    )
    try:
        completed = subprocess.run(
            ["bash", "-c", script],
            check=False,
            capture_output=True,
            text=True,
            timeout=90,
            env={**os.environ, "HOME": str(home)},
            cwd=str(home),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, f"Не удалось измерить диск: {exc}"
    if completed.returncode != 0:
        err = (completed.stderr or completed.stdout or "").strip()[:200]
        return None, f"du завершился с ошибкой" + (f": {err}" if err else "")
    text = (completed.stdout or "").strip().splitlines()
    if not text:
        return None, "Пустой ответ du/awk"
    try:
        return int(text[-1].strip()), None
    except ValueError:
        return None, "Некорректный ответ du/awk"


def _disk_view(
    *,
    used_mib: float | None,
    quota_mib: int,
    note: str | None = None,
    files_url: str | None = None,
) -> dict[str, Any]:
    """Карточка использования диска (квота из формы Админки)."""
    percent: float | None = None
    if used_mib is not None and quota_mib > 0:
        percent = round(100.0 * used_mib / float(quota_mib), 1)
    bar = 0.0 if percent is None else min(100.0, max(0.0, percent))
    return {
        "kind": "disk",
        "used_mib": used_mib,
        "quota_mib": quota_mib,
        "used_label": _format_mib(used_mib),
        "quota_label": _format_mib(float(quota_mib)),
        "percent": percent,
        "bar": bar,
        "note": note,
        "files_url": files_url,
        "hint": (
            "В публичном API нет эндпоинта квоты. Лимит — из настроек модуля "
            "(free: "
            f"{Config.PA_DISC_FREE} МиБ). Занятость — официальная формула PA Disk Quota: "
            "du по /tmp и домашнему каталогу (включая скрытые)."
        ),
    }


def _fetch_disk(settings: PaSettings) -> tuple[PaApiResult, dict[str, Any]]:
    """Диск: локальный du при запуске на PA; иначе квота + пояснение."""
    quota = max(1, int(settings.disk_quota_mib))
    files_url = f"https://{settings.api_host}/user/{settings.username}/files/"
    used_bytes, err = _home_disk_usage_bytes(settings.username)
    if used_bytes is None:
        view = _disk_view(
            used_mib=None,
            quota_mib=quota,
            note=err,
            files_url=files_url,
        )
        # Не ошибка API: квота всё равно полезна; OK=True без data.
        return (
            PaApiResult(ok=True, status_code=None, data={"quota_mib": quota}),
            view,
        )
    used_mib = used_bytes / (1024.0 * 1024.0)
    view = _disk_view(used_mib=used_mib, quota_mib=quota, files_url=files_url)
    return (
        PaApiResult(
            ok=True,
            status_code=None,
            data={"used_bytes": used_bytes, "quota_mib": quota},
        ),
        view,
    )


def _list_rows(items: Any, fields: tuple[tuple[str, str], ...]) -> dict[str, Any]:
    """Таблица из списка dict для шаблона."""
    rows: list[dict[str, str]] = []
    if isinstance(items, list):
        for item in items:
            if not isinstance(item, dict):
                rows.append({"primary": str(item), "secondary": ""})
                continue
            parts: list[str] = []
            primary = ""
            for key, label in fields:
                val = item.get(key)
                if val is None or val == "":
                    continue
                if not primary:
                    primary = str(val)
                else:
                    parts.append(f"{label}: {val}")
            rows.append(
                {
                    "primary": primary or "—",
                    "secondary": " · ".join(parts),
                }
            )
    return {"kind": "list", "count": len(rows), "rows": rows, "empty": not rows}


def _friendly_view(key: str, data: Any) -> dict[str, Any] | None:
    """Преобразовать ответ API в структуру для user-friendly шаблона."""
    if key == "cpu" and isinstance(data, dict):
        return _cpu_view(data)
    if key == "webapps":
        return _list_rows(
            data,
            (
                ("domain_name", "домен"),
                ("python_version", "Python"),
            ),
        )
    if key == "schedule":
        return _list_rows(
            data,
            (
                ("command", "команда"),
                ("enabled", "вкл"),
                ("interval", "интервал"),
                ("description", "описание"),
            ),
        )
    if key == "always_on":
        return _list_rows(
            data,
            (
                ("command", "команда"),
                ("description", "описание"),
                ("enabled", "вкл"),
            ),
        )
    if key == "consoles":
        return _list_rows(
            data,
            (
                ("executable", "команда"),
                ("working_directory", "каталог"),
                ("id", "id"),
            ),
        )
    return {"kind": "raw", "data": data}


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

    raw_quota = (form.get("disk_quota_mib") or "").strip() or str(Config.PA_DISC_FREE)
    try:
        disk_quota_mib = int(raw_quota)
    except ValueError:
        return {}, "Квота диска должна быть целым числом (МиБ)."
    if disk_quota_mib < 1:
        return {}, "Квота диска должна быть не меньше 1 МиБ."

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
        "monitor_disk": form.get("monitor_disk") == "on",
        "disk_quota_mib": disk_quota_mib,
    }, None
