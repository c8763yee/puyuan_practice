

from django.db import models as django_models
from rest_framework import serializers

from api.serializers import create_serializer

from .models import Models
from ..auths.models import UserProfile


UserProfileSerializer = create_serializer(UserProfile)
DefaultSerializer = create_serializer(Models.Default)
SettingSerializer = create_serializer(Models.Setting)


class DefaultSetSerializer(DefaultSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.all(), source='user')

    class Meta:
        model = Models.Default
        exclude = ['user']


class SettingSetSerializer(SettingSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.all(), source='user')

    class Meta:
        model = Models.Setting
        exclude = ['user']


class UserSetSerializer(serializers.ModelSerializer):
    default = DefaultSetSerializer()
    setting = SettingSetSerializer()
    lists = serializers.ListField(
        child=serializers.IntegerField(), source='get_lists')

    class Meta:
        model = Models.UserSet
        exclude = ['user']


BloodPressureSerializer = create_serializer(Models.BloodPressure)
WeightSerializer = create_serializer(Models.Weight)
BloodSugarSerializer = create_serializer(Models.BloodSugar)
