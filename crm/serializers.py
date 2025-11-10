"""DRF serializers for CRM resources."""
from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from crm.models import Client, Interaction, Lead

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]


class ClientSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Client
        fields = [
            "id",
            "name",
            "company",
            "email",
            "phone",
            "website",
            "industry",
            "notes",
            "owner",
            "created_at",
            "updated_at",
        ]


class LeadSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(),
        source="client",
        write_only=True,
    )
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="assigned_to",
        write_only=True,
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Lead
        fields = [
            "id",
            "client",
            "client_id",
            "status",
            "source",
            "assigned_to",
            "assigned_to_id",
            "value",
            "expected_close_date",
            "created_at",
            "updated_at",
        ]


class InteractionSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(),
        source="client",
        write_only=True,
    )
    author = UserSerializer(read_only=True)

    class Meta:
        model = Interaction
        fields = [
            "id",
            "client",
            "client_id",
            "author",
            "interaction_type",
            "subject",
            "notes",
            "occurred_at",
            "follow_up_date",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["author"] = request.user
        return super().create(validated_data)
