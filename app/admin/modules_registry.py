"""Каталог подключаемых модулей админки: категории → модули."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from app.admin import pythonanywhere as pa


@dataclass(frozen=True)
class ModuleInfo:
    """Описание модуля в каталоге."""

    id: str
    title: str
    description: str
    endpoint: str | None = None
    """Flask endpoint настроек; None — ещё не реализован."""
    status_label: Callable[[], str] | None = None


@dataclass(frozen=True)
class ModuleCategory:
    """Категория модулей."""

    id: str
    title: str
    description: str
    modules: tuple[ModuleInfo, ...]


def _pa_status() -> str:
    settings = pa.get_settings()
    if settings.enabled and settings.has_credentials:
        return "включён"
    if settings.has_credentials:
        return "настроен, выключен"
    return "не настроен"


MODULE_CATALOG: tuple[ModuleCategory, ...] = (
    ModuleCategory(
        id="hosting",
        title="Хостинг",
        description="Деплой и мониторинг окружения.",
        modules=(
            ModuleInfo(
                id="pythonanywhere",
                title="PythonAnywhere",
                description=(
                    "API-мониторинг (CPU, webapps, tasks, consoles). "
                    "Учётные данные только через форму модуля."
                ),
                endpoint="admin.pythonanywhere_settings",
                status_label=_pa_status,
            ),
        ),
    ),
    ModuleCategory(
        id="media",
        title="Медиа",
        description="Изображения и вложения.",
        modules=(
            ModuleInfo(
                id="images",
                title="Загрузка изображений",
                description="Загрузка и оптимизация картинок для постов и аватаров.",
            ),
        ),
    ),
    ModuleCategory(
        id="i18n",
        title="Локализация",
        description="Языки интерфейса и контента.",
        modules=(
            ModuleInfo(
                id="locales",
                title="Локали",
                description="Список локалей и переключение языка.",
            ),
        ),
    ),
    ModuleCategory(
        id="account",
        title="Аккаунт",
        description="Подтверждение и профиль пользователя.",
        modules=(
            ModuleInfo(
                id="email_verify",
                title="Подтверждение email",
                description="Верификация аккаунта по электронной почте.",
            ),
        ),
    ),
)


def catalog_for_template() -> list[dict]:
    """Каталог для Jinja: категории с статусами модулей."""
    result: list[dict] = []
    for cat in MODULE_CATALOG:
        modules: list[dict] = []
        for mod in cat.modules:
            status = "скоро"
            if mod.endpoint and mod.status_label:
                status = mod.status_label()
            elif mod.endpoint:
                status = "доступен"
            modules.append(
                {
                    "id": mod.id,
                    "title": mod.title,
                    "description": mod.description,
                    "endpoint": mod.endpoint,
                    "status": status,
                    "available": mod.endpoint is not None,
                }
            )
        result.append(
            {
                "id": cat.id,
                "title": cat.title,
                "description": cat.description,
                "modules": modules,
            }
        )
    return result
