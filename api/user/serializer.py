from django.utils import timezone
from django.forms.models import model_to_dict
from rest_framework import serializers

from api.serializers import create_serializer

from . import models as Models
from ..auths.models import UserProfile


UserProfileSerializer = create_serializer(UserProfile)
DefaultSerializer = create_serializer(Models.Default)
SettingSerializer = create_serializer(Models.Setting)


class DefaultProfileSerializer(DefaultSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.all(), source="user"
    )

    class Meta:
        model = Models.Default
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


class UserSetOutputSerializer(serializers.ModelSerializer):
    # foreign key
    default = serializers.SerializerMethodField()
    setting = serializers.SerializerMethodField()

    # custom output
    height = serializers.SerializerMethodField()
    weight = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    vip = serializers.SerializerMethodField()

    # bool -> int
    verified = serializers.SerializerMethodField()
    must_change_password = serializers.SerializerMethodField()

    # static data
    unread_records = serializers.ListField(default=[0, 0, 0])
    privacy_policy = serializers.IntegerField(default=1)

    def get_verified(self, obj) -> int:
        return int(obj.verified)

    def get_must_change_password(self, obj) -> int:
        return int(obj.must_change_password)

    def get_weight(self, obj) -> float:
        return obj.init_weight

    def get_group(self, obj) -> str:
        return str(obj.group)

    def get_height(self, obj) -> float:
        return obj.init_height

    def get_vip(self, obj) -> dict:
        return {
            "id": 1,
            "user_id": obj.id,
            "level": 0,
            "remark": 0.0,
            "started_at": (now := timezone.now()).strftime("%Y-%m-%d %H:%M:%S"),
            "ended_at": (now + timezone.timedelta(days=365)).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def get_setting(self, obj) -> dict:
        user_setting = Models.Setting.objects.get(user=obj.id)
        return {
            "id": user_setting.id,  # type: ignore
            "user_id": user_setting.user.id,
            "after_recording": int(user_setting.after_recording),
            "no_recording_for_a_day": int(user_setting.no_recording_for_a_day),
            "over_max_or_under_min": int(user_setting.over_max_or_under_min),
            "after_meal": int(user_setting.after_meal),
            "unit_of_sugar": int(user_setting.unit_of_sugar),
            "unit_of_weight": int(user_setting.unit_of_weight),
            "unit_of_height": int(user_setting.unit_of_height),
            "created_at": user_setting.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": user_setting.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def get_default(self, obj) -> dict:
        user_default = Models.Default.objects.get(user=obj.id)
        user_default_dict = model_to_dict(user_default, exclude=["user"])
        user_default_dict["user_id"] = user_default.user.id
        user_default_dict["created_at"] = user_default.created_at.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        user_default_dict["updated_at"] = user_default.updated_at.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        return user_default_dict

    def get_gender(self, obj) -> int:
        return int(obj.gender)

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "name",
            "account",
            "email",
            "phone",
            "fb_id",
            "status",
            "group",
            "birthday",
            "height",
            "weight",
            "gender",
            "address",
            "unread_records",
            "verified",
            "privacy_policy",
            "must_change_password",
            "fcm_id",
            "login_times",
            "created_at",
            "updated_at",
            "default",
            "setting",
            "vip",
        ]
