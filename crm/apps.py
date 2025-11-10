"""Configuration for the CRM application."""
from __future__ import annotations

from django.apps import AppConfig


class CrmConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "crm"

    def ready(self) -> None:  # pragma: no cover - imported for side effects
        import crm.signals  # noqa: F401
