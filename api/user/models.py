from django.db import models
# Create your models here.


class BaseUser(models.Model):
    class Meta:
        abstract = True
        app_label = 'user'


class UserProfile(BaseUser):
    ID = models.AutoField(primary_key=True)
    user_id = models.ForeignKey('api.auths.Auth', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    birthday = models.DateField()
    height = models.FloatField()
    weight = models.CharField(max_length=10)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    gender = models.BooleanField()
    fcm_id = models.CharField(max_length=100)
    address = models.CharField(max_length=100)


class UserSet(BaseUser):
    pass


class DefaultSet(BaseUser):
    user_id = models.ForeignKey(
        'api.auths.Auth', on_delete=models.CASCADE, unique=True)
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


class Setting(BaseUser):
    after_recoding = models.BooleanField()
    no_recording_for_a_day = models.BooleanField()
    over_max_or_under_min = models.BooleanField()
    after_meal = models.BooleanField()
    unit_of_sugar = models.BooleanField()
