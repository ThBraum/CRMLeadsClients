"""Forms for CRM operations."""
from __future__ import annotations

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from crm.models import Client, Interaction, Lead, Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["phone", "position", "avatar"]
        widgets = {
            "phone": forms.TextInput(attrs={"class": "form-input"}),
            "position": forms.TextInput(attrs={"class": "form-input"}),
            "avatar": forms.URLInput(attrs={"class": "form-input"}),
        }


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            "name",
            "company",
            "email",
            "phone",
            "website",
            "industry",
            "notes",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 4}),
        }


class LeadForm(forms.ModelForm):
    expected_close_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    class Meta:
        model = Lead
        fields = [
            "client",
            "status",
            "source",
            "assigned_to",
            "value",
            "expected_close_date",
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].queryset = User.objects.filter(is_active=True)
        if user and not user.is_superuser:
            self.fields["client"].queryset = Client.objects.filter(owner=user)


class InteractionForm(forms.ModelForm):
    occurred_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
    )

    class Meta:
        model = Interaction
        fields = [
            "client",
            "interaction_type",
            "subject",
            "notes",
            "occurred_at",
            "follow_up_date",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 4}),
            "follow_up_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user and not user.is_superuser:
            self.fields["client"].queryset = Client.objects.filter(owner=user)


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def save(self, commit: bool = True) -> User:
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user
