#!/usr/bin/env python3
"""stop-hook: если реализация на task-ветке без docs — follow-up на flask-blog-docs-after-task."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

DOC_TARGETS = (
    "docs/ARCHITECTURE.md",
    "docs/DEVELOPMENT.md",
    "docs/DEPLOY.md",
    "docs/CHANGELOG.md",
    "docs/README.md",
    "AGENTS.md",
)

COMPLETION_HINT = re.compile(
    r"(?is)("
    r"\bготово\b|\bзаверш|\bфинализ|"
    r"\bdone\b|\bcomplete[d]?\b|"
    r"создал\s+PR|создан\s+PR|\bPR\b.*https?://|"
    r"можно\s+(делать\s+)?PR|готов[аоы]\s+к\s+(PR|пуш|merge)|"
    r"working tree clean|nothing to commit|"
    r"все подзадачи|реализация\s+завершена"
    r")"
)

FOLLOWUP = (
    "Перед завершением задачи обязательно выполни skill "
    "`.cursor/skills/flask-blog-docs-after-task/SKILL.md` "
    "(pointer в `.cursor/rules/00-project.mdc`): "
    "прочитай skill целиком (Read), обнови релевантные docs/CHANGELOG/AGENTS "
    "по таблице skill и закоммить по его правилам. "
    "Не пропускай этот шаг и не жди отдельной просьбы пользователя."
)


def run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


def git_out(root: Path, *args: str) -> str:
    return (run_git(root, *args).stdout or "").strip()


def ref_ok(root: Path, ref: str) -> bool:
    return run_git(root, "rev-parse", "--verify", ref).returncode == 0


def changed_files(root: Path, base: str) -> set[str]:
    names: set[str] = set()
    for args in (
        ("diff", "--name-only", f"{base}...HEAD"),
        ("diff", "--name-only"),
        ("diff", "--name-only", "--cached"),
    ):
        out = git_out(root, *args)
        if out:
            names.update(line.strip() for line in out.splitlines() if line.strip())
    return names


def is_app_change(path: str) -> bool:
    return (
        path.startswith("app/")
        or path.startswith("migrations/")
        or path.startswith("tests/")
        or path
        in {
            "schema.sql",
            "pyproject.toml",
            "requirements.txt",
            "wsgi.py",
        }
    )


def is_doc_sync(path: str) -> bool:
    return path in DOC_TARGETS


def last_assistant_text(transcript_path: str | None) -> str:
    if not transcript_path:
        return ""
    path = Path(transcript_path)
    if not path.is_file():
        return ""
    try:
        data = path.read_bytes()
        if len(data) > 400_000:
            data = data[-400_000:]
        text = data.decode("utf-8", errors="ignore")
    except OSError:
        return ""

    chunks: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        content = event.get("content") or event.get("message") or event.get("text")
        role = str(event.get("role") or event.get("type") or "").lower()
        if content is None:
            continue
        if role and ("assistant" not in role) and role not in {"message", "ai"}:
            # keep unknown roles if they look like final assistant blobs
            if "assistant" not in json.dumps(event, ensure_ascii=False).lower()[:200]:
                continue
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, dict):
                    parts.append(str(item.get("text") or ""))
                elif isinstance(item, str):
                    parts.append(item)
            content = "\n".join(parts)
        if isinstance(content, str) and content.strip():
            chunks.append(content)
    return chunks[-1] if chunks else text[-8000:]


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        print("{}")
        return 0

    if payload.get("status") != "completed":
        print("{}")
        return 0
    if int(payload.get("loop_count") or 0) >= 1:
        print("{}")
        return 0

    roots = payload.get("workspace_roots") or []
    root = Path(roots[0]) if roots else Path.cwd()
    if not (root / ".cursor/skills/flask-blog-docs-after-task/SKILL.md").is_file():
        print("{}")
        return 0

    branch = git_out(root, "branch", "--show-current")
    if not branch.startswith(("feat/", "fix/", "chore/")):
        print("{}")
        return 0

    if ref_ok(root, "origin/dev"):
        base = "origin/dev"
    elif ref_ok(root, "dev"):
        base = "dev"
    else:
        print("{}")
        return 0

    files = changed_files(root, base)
    has_app = any(is_app_change(f) for f in files)
    has_docs = any(is_doc_sync(f) for f in files)
    if not has_app or has_docs:
        print("{}")
        return 0

    assistant = last_assistant_text(payload.get("transcript_path"))
    if not COMPLETION_HINT.search(assistant):
        print("{}")
        return 0

    print(json.dumps({"followup_message": FOLLOWUP}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        print("{}")
        raise SystemExit(0)
