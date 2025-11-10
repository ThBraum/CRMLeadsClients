"""URL routes for CRM functionality."""
from __future__ import annotations

from django.urls import path

from crm import views

app_name = "crm"

urlpatterns = [
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("profile/", views.ProfileUpdateView.as_view(), name="profile"),
    path("pipeline/", views.PipelineBoardView.as_view(), name="pipeline"),
    path("clients/", views.ClientListView.as_view(), name="client-list"),
    path("clients/new/", views.ClientCreateView.as_view(), name="client-create"),
    path("clients/<int:pk>/", views.ClientDetailView.as_view(), name="client-detail"),
    path("clients/<int:pk>/edit/", views.ClientUpdateView.as_view(), name="client-update"),
    path(
        "clients/<int:client_pk>/interactions/new/",
        views.InteractionCreateView.as_view(),
        name="interaction-create",
    ),
    path(
        "interactions/<int:pk>/complete/",
        views.mark_interaction_completed,
        name="interaction-complete",
    ),
    path("leads/", views.LeadListView.as_view(), name="lead-list"),
    path("leads/new/", views.LeadCreateView.as_view(), name="lead-create"),
    path("leads/<int:pk>/", views.LeadDetailView.as_view(), name="lead-detail"),
    path("leads/<int:pk>/edit/", views.LeadUpdateView.as_view(), name="lead-update"),
    path("leads/<int:pk>/stage/", views.LeadStageUpdateView.as_view(), name="lead-stage"),
]
