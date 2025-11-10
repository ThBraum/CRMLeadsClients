"""REST API endpoints for the CRM app."""
from __future__ import annotations

from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.routers import DefaultRouter

from crm.models import Client, Interaction, Lead
from crm.serializers import ClientSerializer, InteractionSerializer, LeadSerializer

router = DefaultRouter()


class ClientViewSet(viewsets.ModelViewSet):
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):  # type: ignore[override]
        qs = Client.objects.select_related("owner")
        user = self.request.user
        if user.is_superuser:
            return qs
        return qs.filter(owner=user)

    def perform_create(self, serializer):  # type: ignore[override]
        serializer.save(owner=self.request.user)


class LeadViewSet(viewsets.ModelViewSet):
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):  # type: ignore[override]
        qs = Lead.objects.select_related("client", "assigned_to")
        user = self.request.user
        if user.is_superuser:
            return qs
        return qs.filter(Q(assigned_to=user) | Q(client__owner=user))


class InteractionViewSet(viewsets.ModelViewSet):
    serializer_class = InteractionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):  # type: ignore[override]
        qs = Interaction.objects.select_related("client", "author")
        user = self.request.user
        if user.is_superuser:
            return qs
        return qs.filter(Q(client__owner=user) | Q(author=user))

    def perform_create(self, serializer):  # type: ignore[override]
        serializer.save(author=self.request.user)


router.register("clients", ClientViewSet, basename="client")
router.register("leads", LeadViewSet, basename="lead")
router.register("interactions", InteractionViewSet, basename="interaction")

urlpatterns = router.urls
