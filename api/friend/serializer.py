from rest_framework import serializers

from api.serializers import create_serializer

from . import models as Models

from ..user.serializer import UserSetSerializer
from ..user.models import UserSet


class ListSerializer(serializers.ModelSerializer):
    name = serializers.PrimaryKeyRelatedField(
        queryset=UserSet.objects.all(), source="user"
    )
    account = serializers.PrimaryKeyRelatedField(
        queryset=UserSet.objects.all(), source="user"
    )

    class Meta:
        model = Models.Relation
        fields = ["id", "name", "account"]


Send = create_serializer(
    Models.Relation,
    fields=["relation_type", "invite_code"],
)


class RelationSerializer(serializers.ModelSerializer):
    user = UserSetSerializer()

    class Meta:
        model = Models.Relation
        fields = ["id", "name", "account"]


class RequestSerializer(serializers.ModelSerializer):
    relation_id = serializers.PrimaryKeyRelatedField(
        queryset=Models.Relation.objects.all(), source="relation"
    )

    class Meta:
        model = Models.Relation
        fields = ["id", "name", "relation_type", "status", "read"]

    user = RelationSerializer()


class ResultSerializer(serializers.ModelSerializer):
    relation_id = serializers.PrimaryKeyRelatedField(
        queryset=Models.Relation.objects.all(), source="relation"
    )
    relation = RelationSerializer()

    class Meta:
        model = Models.Relation
        exclude = ["relation"]

    relation = RelationSerializer()
