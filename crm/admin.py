"""Admin registrations for CRM models."""
from __future__ import annotations

from django.contrib import admin

from crm.models import Client, Interaction, Lead, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "position")
    search_fields = ("user__username", "user__email", "phone", "position")


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "email", "owner", "created_at")
    list_filter = ("owner", "industry")
    search_fields = ("name", "company", "email", "phone")


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("client", "status", "assigned_to", "value", "expected_close_date")
    list_filter = ("status", "assigned_to")
    search_fields = ("client__name", "source")


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ("client", "interaction_type", "author", "occurred_at")
    list_filter = ("interaction_type", "occurred_at")
    search_fields = ("client__name", "notes", "subject")
    autocomplete_fields = ("client", "author")
