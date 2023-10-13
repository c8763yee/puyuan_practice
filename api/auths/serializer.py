from rest_framework import serializers

from api.serializers import create_serializer

from .models import UserProfile


class Register(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["email", "password"]

    def save(self, **kwargs):
        user = UserProfile.objects.create(**self.validated_data)
        user.is_active = False
        user.set_password(self.validated_data["password"])
        user.save()


class Login(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["email", "password"]

    def is_valid(self, *, raise_exception=False) -> tuple[UserProfile | None, bool]:
        super_valid = super().is_valid(raise_exception=raise_exception)
        if super_valid:
            user = UserProfile.objects.get(email=self.validated_data["email"])
            check_password = user.check_password(self.validated_data["password"])

        if super_valid is False or check_password is False or user.is_active is False:
            if raise_exception:
                raise serializers.ValidationError("validation error")
            return None, False

        return user, True
