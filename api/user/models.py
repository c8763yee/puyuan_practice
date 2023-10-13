from django.db import models

# Create your models here.
from api.models import BaseSetting, BaseUserData


class UserSet(BaseSetting):
    name = models.CharField(max_length=50)
    birthday = models.DateField(null=True)
    height = models.FloatField(default=0.0)
    gender = models.BooleanField(default=True)
    fcm_id = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    weight = models.CharField(max_length=10)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    default = models.OneToOneField(
        "user.Default",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    setting = models.OneToOneField(
        "user.Setting",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )


class Default(BaseSetting):
    sugar_delta_max = models.FloatField(default=10.0)
    sugar_delta_min = models.FloatField(default=1.0)
    sugar_morning_max = models.FloatField(default=10.0)
    sugar_morning_min = models.FloatField(default=1.0)
    sugar_evening_max = models.FloatField(default=10.0)
    sugar_evening_min = models.FloatField(default=1.0)
    sugar_before_max = models.FloatField(default=10.0)
    sugar_before_min = models.FloatField(default=1.0)
    sugar_after_max = models.FloatField(default=10.0)
    sugar_after_min = models.FloatField(default=1.0)
    systolic_max = models.IntegerField(default=10)
    systolic_min = models.IntegerField(default=1)
    diastolic_max = models.IntegerField(default=10)
    diastolic_min = models.IntegerField(default=1)
    pulse_max = models.IntegerField(default=10)
    pulse_min = models.IntegerField(default=1)
    weight_max = models.FloatField(default=10.0)
    weight_min = models.FloatField(default=1.0)
    bmi_max = models.FloatField(default=10.0)
    bmi_min = models.FloatField(default=1.0)
    body_fat_max = models.FloatField(default=10.0)
    body_fat_min = models.FloatField(default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Setting(BaseSetting):
    after_recording = models.BooleanField(default=False)
    no_recording_for_a_day = models.BooleanField(default=False)
    over_max_or_under_min = models.BooleanField(default=True)
    after_meal = models.BooleanField(default=True)
    unit_of_sugar = models.BooleanField(default=True)
    unit_of_weight = models.BooleanField(default=True)
    unit_of_height = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BloodPressure(BaseUserData):
    systolic = models.IntegerField()
    diastolic = models.IntegerField()
    pulse = models.IntegerField()
    recorded_at = models.DateTimeField(auto_now_add=True)


class Weight(BaseUserData):
    weight = models.FloatField()
    bmi = models.FloatField()
    body_fat = models.FloatField()
    recorded_at = models.DateTimeField(auto_now_add=True)


class BloodSugar(BaseUserData):
    sugar = models.FloatField()
    timeperiod = models.IntegerField()
    recorded_at = models.DateTimeField(auto_now_add=True)
    drug = models.IntegerField()
    exercise = models.IntegerField()


class Diet(BaseUserData):
    description = models.CharField(max_length=100)
    meal = models.IntegerField()
    tag = models.CharField(max_length=100)
    image = models.IntegerField()
    lat = models.FloatField()
    lng = models.FloatField()
    recorded_at = models.DateTimeField(auto_now_add=True)


class A1c(BaseUserData):
    a1c = models.IntegerField()
    recorded_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Medical(BaseSetting):
    diabetes_type = models.IntegerField(default=1)
    oad = models.BooleanField(default=True)
    insulin = models.BooleanField(default=True)
    anti_hypertensives = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Drug(BaseUserData):
    name = models.CharField(max_length=100)
    type = models.IntegerField()
    recorded_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Care(BaseUserData):
    reply_id = models.IntegerField(default=0)
    message = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
