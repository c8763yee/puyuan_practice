from rest_framework import serializers

from api.serializers import create_serializer

from . import models as Models
from ..auths.models import UserProfile


UserProfileSerializer = create_serializer(UserProfile)
DefaultSerializer = create_serializer(Models.Default)
SettingSerializer = create_serializer(Models.Setting)


class DefaultSetSerializer(DefaultSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.all(), source="user"
    )

    class Meta:
        model = Models.Default
        exclude = ["user"]


class SettingSetSerializer(SettingSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.all(), source="user"
    )

    class Meta:
        model = Models.Setting
        exclude = ["user"]


class UserSetSerializer(serializers.ModelSerializer):
    default = DefaultSetSerializer()
    setting = SettingSetSerializer()

    # account related to UserSet.email
    account = serializers.SerializerMethodField()

    def get_account(self, obj):
        return obj.email

    class Meta:
        model = Models.UserSet
        exclude = ["user"]


BloodPressureSerializer = create_serializer(Models.BloodPressure)
WeightSerializer = create_serializer(Models.Weight)
BloodSugarSerializer = create_serializer(Models.BloodSugar)


class DietSerializer(serializers.ModelSerializer):
    # modify tag field for store list data as string that split by ','
    tag = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = Models.Diet
        fields = "__all__"

    def save(self, **kwargs):
        # Convert data in tag field from list to string that is split by ','
        tag = self.validated_data.get("tag")  # type: ignore
        if tag:
            self.validated_data["tag"] = ", ".join(tag)  # type: ignore
        return super().save(**kwargs)

    def to_representation(self, instance):
        # Convert data in tag field from string that is split by ',' to list
        ret = super().to_representation(instance)
        ret["tag"] = ret["tag"].split(", ")
        return ret


A1cSerializer = create_serializer(
    Models.A1c,
    foreign_key={
        "user_id": serializers.PrimaryKeyRelatedField(
            queryset=UserProfile.objects.all(), source="user"
        )
    },
    exclude=["user"],
)

MedicalSerializer = create_serializer(Models.Medical)

DrugSerializer = create_serializer(
    Models.Drug,
    foreign_key={
        "user_id": serializers.PrimaryKeyRelatedField(
            queryset=UserProfile.objects.all(), source="user"
        )
    },
    exclude=["user"],
)

CareSerializer = create_serializer(
    Models.Care,
    foreign_key={
        "user_id": serializers.PrimaryKeyRelatedField(
            queryset=UserProfile.objects.all(), source="user"
        ),
        "member_id": serializers.IntegerField(default=1),
    },
    exclude=["user"],
)
