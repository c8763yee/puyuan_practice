from django.contrib.auth.hashers import make_password, make_password
from rest_framework import serializers

from api.serializers import create_serializer

from . import models as Models


class Register(serializers.ModelSerializer):
    class Meta:
        model = Models.UserProfile
        fields = ["email", "password"]

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super(Register, self).create(validated_data)


class Login(serializers.ModelSerializer):
    class Meta:
        model = Models.UserProfile
        fields = ["email", "password"]


News = create_serializer(Models.News)
Share = create_serializer(
    Models.UserRecord, apply_fields=["id", "type", "relation_type"]
)
CheckShare = create_serializer(Models.UserRecord, exclude=["user", "UID"])
