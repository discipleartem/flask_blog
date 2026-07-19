"""Deploy hook: git pull + deps + migrations (PythonAnywhere)."""

from __future__ import annotations

import logging
import secrets
import subprocess
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request

from app.config import BASE_DIR

bp = Blueprint("deploy", __name__)
logger = logging.getLogger(__name__)

_TIMEOUT_SEC = 120


def _authorized(expected: str) -> bool:
    """Проверка Bearer-токена (timing-safe)."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return False
    token = auth.removeprefix("Bearer ").strip()
    if not token or not expected:
        return False
    if len(token) != len(expected):
        return False
    return secrets.compare_digest(token, expected)


def _run_step(cmd: list[str], cwd: Path) -> dict[str, object]:
    """Запуск одной команды деплоя."""
    completed = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=_TIMEOUT_SEC,
        check=False,
    )
    return {
        "cmd": cmd,
        "returncode": completed.returncode,
        "stdout": (completed.stdout or "")[-4000:],
        "stderr": (completed.stderr or "")[-4000:],
    }


def run_deploy(project_root: Path) -> tuple[bool, list[dict[str, object]]]:
    """Выполнить шаги обновления кода на сервере.

    Returns:
        (ok, steps) — ok=False, если любой шаг завершился с ошибкой.
    """
    venv_bin = project_root / ".venv" / "bin"
    pip = str(venv_bin / "pip")
    flask_bin = str(venv_bin / "flask")
    steps_spec: list[list[str]] = [
        ["git", "pull", "origin", "main"],
        [pip, "install", "-r", "requirements.txt"],
        [flask_bin, "--app", "wsgi", "db-upgrade"],
    ]
    results: list[dict[str, object]] = []
    for cmd in steps_spec:
        try:
            result = _run_step(cmd, project_root)
        except subprocess.TimeoutExpired:
            results.append(
                {
                    "cmd": cmd,
                    "returncode": -1,
                    "stdout": "",
                    "stderr": f"timeout after {_TIMEOUT_SEC}s",
                }
            )
            return False, results
        results.append(result)
        if int(result["returncode"]) != 0:
            return False, results
    return True, results


@bp.post("/internal/deploy")
def deploy() -> tuple[object, int]:
    """Защищённый hook для авто-деплоя с GitHub Actions."""
    expected = current_app.config.get("DEPLOY_SECRET") or ""
    if not expected:
        return jsonify({"error": "deploy disabled"}), 404
    if not _authorized(expected):
        return jsonify({"error": "unauthorized"}), 401

    ok, steps = run_deploy(BASE_DIR)
    if not ok:
        logger.error("Deploy failed: %s", steps)
        return jsonify({"ok": False, "steps": steps}), 500

    logger.info("Deploy succeeded")
    return jsonify({"ok": True, "steps": steps}), 200
