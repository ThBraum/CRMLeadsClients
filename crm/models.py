"""Data models for the CRM domain."""
from __future__ import annotations

from datetime import date

from django.conf import settings
from django.db import models
from django.urls import reverse

User = settings.AUTH_USER_MODEL


class Profile(models.Model):
    """Stores contact details for each platform user."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=20, blank=True)
    position = models.CharField(max_length=100, blank=True)
    avatar = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user__username"]

    def __str__(self) -> str:
        return self.user.get_full_name() or self.user.username


class Client(models.Model):
    """Represents an organization or person with an ongoing relationship."""

    name = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="clients",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("name", "owner")

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("crm:client-detail", args=[self.pk])


class LeadStatus(models.TextChoices):
    NEW = "new", "Novo"
    CONTACT = "contact", "Contato"
    PROPOSAL = "proposal", "Proposta"
    WON = "won", "Fechado"
    LOST = "lost", "Perdido"


class Lead(models.Model):
    """Sales pipeline entry for a potential deal."""

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="leads")
    status = models.CharField(max_length=20, choices=LeadStatus.choices, default=LeadStatus.NEW)
    source = models.CharField(max_length=120, blank=True)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="leads",
        null=True,
        blank=True,
    )
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expected_close_date = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["assigned_to", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.client.name} - {self.get_status_display()}"

    def is_overdue(self) -> bool:
        return bool(self.expected_close_date and self.expected_close_date < date.today())

    def get_absolute_url(self) -> str:
        return reverse("crm:lead-detail", args=[self.pk])


class InteractionType(models.TextChoices):
    CALL = "call", "Chamada"
    EMAIL = "email", "E-mail"
    MEETING = "meeting", "Reunião"
    NOTE = "note", "Nota"


class Interaction(models.Model):
    """Chronological log of touchpoints with a client."""

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="interactions")
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="interactions",
        null=True,
        blank=True,
    )
    interaction_type = models.CharField(
        max_length=20,
        choices=InteractionType.choices,
        default=InteractionType.NOTE,
    )
    subject = models.CharField(max_length=255, blank=True)
    notes = models.TextField()
    occurred_at = models.DateTimeField()
    follow_up_date = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-occurred_at"]

    def __str__(self) -> str:
        return f"{self.client.name} ({self.get_interaction_type_display()})"

    def get_absolute_url(self) -> str:
        return reverse("crm:client-detail", args=[self.client_id])
