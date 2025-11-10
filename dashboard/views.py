"""Dashboard views for analytics."""
from __future__ import annotations

from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Sum
from django.utils import timezone
from django.views.generic import TemplateView

from crm.models import Client, Interaction, Lead, LeadStatus


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):  # type: ignore[override]
        context = super().get_context_data(**kwargs)
        user = self.request.user

        clients_qs = Client.objects.all()
        leads_qs = Lead.objects.all()
        interactions_qs = Interaction.objects.all()

        if not user.is_superuser:
            clients_qs = clients_qs.filter(owner=user)
            leads_qs = leads_qs.filter(Q(assigned_to=user) | Q(client__owner=user))
            interactions_qs = interactions_qs.filter(Q(author=user) | Q(client__owner=user))

        pipeline = leads_qs.values("status").annotate(total=Count("id"), amount=Sum("value"))
        status_map = {status: 0 for status, _ in LeadStatus.choices}
        value_map: dict[str, Decimal | float] = {status: 0 for status, _ in LeadStatus.choices}
        for row in pipeline:
            status_map[row["status"]] = row["total"]
            value_map[row["status"]] = row["amount"] or Decimal("0")

        won_leads = leads_qs.filter(status=LeadStatus.WON)
        total_leads = leads_qs.count() or 1
        conversion_rate = (won_leads.count() / total_leads) * 100

        sales_by_user = (
            leads_qs.filter(status=LeadStatus.WON)
            .values("assigned_to__username")
            .annotate(total=Sum("value"))
            .order_by("assigned_to__username")
        )

        recent_interactions = interactions_qs.select_related("client", "author")[:10]

        context.update(
            {
                "clients_total": clients_qs.count(),
                "leads_total": leads_qs.count(),
                "interactions_total": interactions_qs.count(),
                "conversion_rate": round(conversion_rate, 2),
                "pipeline_labels": [label for _, label in LeadStatus.choices],
                "pipeline_totals": [status_map[key] for key, _ in LeadStatus.choices],
                "pipeline_values": [float(value_map[key]) for key, _ in LeadStatus.choices],
                "sales_labels": [row["assigned_to__username"] or "Não atribuído" for row in sales_by_user],
                "sales_totals": [float(row["total"] or 0) for row in sales_by_user],
                "recent_interactions": recent_interactions,
                "now": timezone.now(),
            }
        )
        return context
