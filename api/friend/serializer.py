from rest_framework import serializers

from api.serializers import create_serializer

from . import models as Models

from ..user.serializer import UserSetSerializer
from ..user.models import UserSet


Send = create_serializer(
    Models.Relation,
    fields=["relation_type", "invite_code"],
)


class RelationSerializer(serializers.ModelSerializer):
    relation = serializers.SerializerMethodField()

    def get_relation(self, obj):
        user_set = obj.user.user_set
        user_set_data = UserSetSerializer(user_set, many=True).data
        return {"id": obj.id, "user_set": user_set_data}

    class Meta:
        model = Models.Relation
        fields = ["relation"]


class RequestSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=UserSet.objects.all(), source="user"
    )
    relation_id = serializers.PrimaryKeyRelatedField(
        queryset=Models.Relation.objects.all(), source="relation"
    )

    def get_user(self, obj):
        user = obj.user
        user_set = UserSet.objects.filter(user=user).only("name", "email").first()
        return {"id": user.id, "name": user_set.name, "account": user_set.email}

    class Meta:
        model = Models.Relation
        exclude = ["relation", "invite_code"]

    user = serializers.SerializerMethodField()


class ResultSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=UserSet.objects.all(), source="user"
    )

    relation_id = serializers.PrimaryKeyRelatedField(
        queryset=Models.Relation.objects.all(), source="relation"
    )

    def get_relation(self, obj):
        # get id, name, email from related UserSet object
        user = obj.user
        user_set = UserSet.objects.filter(user=user).only("name", "email").first()
        return {"id": user.id, "name": user_set.name, "account": user_set.email}

    class Meta:
        model = Models.Relation
        exclude = ["user", "invite_code"]

    relation = serializers.SerializerMethodField()
