"""Views for CRM operations."""
from __future__ import annotations

from datetime import datetime

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView, View

from crm.forms import ClientForm, InteractionForm, LeadForm, ProfileForm, SignUpForm
from crm.models import Client, Interaction, Lead, LeadStatus, Profile


class RoleRequiredMixin(UserPassesTestMixin):
    """Allow access to admins or superusers only."""

    allowed_roles = {"Admin"}

    def test_func(self) -> bool:
        if self.request.user.is_superuser:
            return True
        profile: Profile | None = getattr(self.request.user, "profile", None)
        return bool(profile and profile.position in self.allowed_roles)

    def handle_no_permission(self):  # type: ignore[override]
        messages.error(self.request, "Você não tem permissão para acessar este recurso.")
        return redirect("dashboard:index")


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "crm/client_list.html"
    context_object_name = "clients"
    paginate_by = 15

    def get_queryset(self):  # type: ignore[override]
        qs = super().get_queryset().select_related("owner")
        if not self.request.user.is_superuser:
            qs = qs.filter(owner=self.request.user)
        search = self.request.GET.get("q")
        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(company__icontains=search)
                | Q(email__icontains=search)
                | Q(phone__icontains=search)
            )
        return qs


class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = "crm/client_detail.html"
    context_object_name = "client"

    def get_queryset(self):  # type: ignore[override]
        qs = super().get_queryset().select_related("owner").prefetch_related("interactions", "leads")
        if self.request.user.is_superuser:
            return qs
        return qs.filter(owner=self.request.user)


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "crm/client_form.html"

    def form_valid(self, form):  # type: ignore[override]
        form.instance.owner = self.request.user
        messages.success(self.request, "Cliente criado com sucesso.")
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "crm/client_form.html"

    def get_queryset(self):  # type: ignore[override]
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(owner=self.request.user)

    def form_valid(self, form):  # type: ignore[override]
        messages.success(self.request, "Cliente atualizado com sucesso.")
        return super().form_valid(form)


class LeadListView(LoginRequiredMixin, ListView):
    model = Lead
    template_name = "crm/lead_list.html"
    context_object_name = "leads"
    paginate_by = 15

    def get_queryset(self):  # type: ignore[override]
        qs = (
            super()
            .get_queryset()
            .select_related("client", "assigned_to")
            .annotate(interaction_count=Count("client__interactions"))
        )
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        if not self.request.user.is_superuser:
            qs = qs.filter(Q(assigned_to=self.request.user) | Q(client__owner=self.request.user))
        return qs

    def get_context_data(self, **kwargs):  # type: ignore[override]
        context = super().get_context_data(**kwargs)
        context["statuses"] = LeadStatus.choices
        return context


class LeadDetailView(LoginRequiredMixin, DetailView):
    model = Lead
    template_name = "crm/lead_detail.html"
    context_object_name = "lead"

    def get_queryset(self):  # type: ignore[override]
        qs = super().get_queryset().select_related("client", "assigned_to")
        if self.request.user.is_superuser:
            return qs
        return qs.filter(Q(assigned_to=self.request.user) | Q(client__owner=self.request.user))


class LeadCreateView(LoginRequiredMixin, CreateView):
    model = Lead
    form_class = LeadForm
    template_name = "crm/lead_form.html"

    def get_form_kwargs(self):  # type: ignore[override]
        kwargs = super().get_form_kwargs()
        if not self.request.user.is_superuser:
            kwargs.setdefault("initial", {})
            kwargs["initial"].setdefault("assigned_to", self.request.user)
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):  # type: ignore[override]
        messages.success(self.request, "Lead criado com sucesso.")
        return super().form_valid(form)


class LeadUpdateView(LoginRequiredMixin, UpdateView):
    model = Lead
    form_class = LeadForm
    template_name = "crm/lead_form.html"

    def get_queryset(self):  # type: ignore[override]
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(Q(assigned_to=self.request.user) | Q(client__owner=self.request.user))

    def form_valid(self, form):  # type: ignore[override]
        messages.success(self.request, "Lead atualizado com sucesso.")
        return super().form_valid(form)

    def get_form_kwargs(self):  # type: ignore[override]
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class LeadStageUpdateView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):  # type: ignore[override]
        lead = Lead.objects.filter(pk=kwargs.get("pk")).select_related("client").first()
        if not lead:
            messages.error(request, "Lead não encontrado.")
            return redirect("crm:lead-list")
        if not request.user.is_superuser and request.user not in {lead.client.owner, lead.assigned_to}:
            messages.error(request, "Você não pode editar este lead.")
            return redirect("crm:lead-detail", pk=lead.pk)
        new_status = request.POST.get("status")
        if new_status not in dict(LeadStatus.choices):
            messages.error(request, "Status inválido.")
            return redirect("crm:lead-detail", pk=lead.pk)
        lead.status = new_status
        lead.save(update_fields=["status", "updated_at"])
        messages.success(request, "Pipeline atualizado.")
        return redirect("crm:lead-detail", pk=lead.pk)


class InteractionCreateView(LoginRequiredMixin, CreateView):
    model = Interaction
    form_class = InteractionForm
    template_name = "crm/interaction_form.html"

    def get_initial(self):  # type: ignore[override]
        initial = super().get_initial()
        client_id = self.kwargs.get("client_pk")
        if client_id:
            initial["client"] = Client.objects.filter(pk=client_id).first()
        initial.setdefault("occurred_at", timezone.now())
        return initial

    def form_valid(self, form):  # type: ignore[override]
        form.instance.author = self.request.user
        messages.success(self.request, "Interação registrada.")
        response = super().form_valid(form)
        return response

    def get_success_url(self):  # type: ignore[override]
        return self.object.client.get_absolute_url()

    def get_context_data(self, **kwargs):  # type: ignore[override]
        context = super().get_context_data(**kwargs)
        client_id = self.kwargs.get("client_pk")
        context["client"] = Client.objects.filter(pk=client_id).first() if client_id else None
        return context

    def get_form_kwargs(self):  # type: ignore[override]
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "crm/profile_form.html"

    def get_object(self):  # type: ignore[override]
        return self.request.user.profile

    def form_valid(self, form):  # type: ignore[override]
        messages.success(self.request, "Perfil atualizado.")
        return super().form_valid(form)

    def get_success_url(self):  # type: ignore[override]
        return reverse_lazy("dashboard:index")


class SignUpView(CreateView):
    model = User
    form_class = SignUpForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("dashboard:index")

    def form_valid(self, form):  # type: ignore[override]
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, "Bem-vindo ao clientesCRM!")
        return response


class PipelineBoardView(LoginRequiredMixin, TemplateView):
    template_name = "crm/pipeline_board.html"

    def get_context_data(self, **kwargs):  # type: ignore[override]
        context = super().get_context_data(**kwargs)
        queryset = Lead.objects.select_related("client", "assigned_to")
        if not self.request.user.is_superuser:
            queryset = queryset.filter(
                Q(assigned_to=self.request.user) | Q(client__owner=self.request.user)
            )
        board = {status: [] for status, _ in LeadStatus.choices}
        for lead in queryset:
            board.setdefault(lead.status, []).append(lead)
        columns = [
            {
                "key": key,
                "label": label,
                "leads": board.get(key, []),
            }
            for key, label in LeadStatus.choices
        ]
        context.update({"columns": columns, "statuses": LeadStatus.choices})
        return context


def mark_interaction_completed(request, pk: int):
    interaction = Interaction.objects.filter(pk=pk, author=request.user).first()
    if interaction:
        interaction.follow_up_date = None
        interaction.notes += f"\n\nFinalizado em {datetime.now():%d/%m/%Y %H:%M}"  # keep audit trail.
        interaction.save(update_fields=["follow_up_date", "notes", "updated_at"])
        messages.success(request, "Interação marcada como concluída.")
    return redirect("crm:client-detail", pk=interaction.client_id if interaction else pk)
