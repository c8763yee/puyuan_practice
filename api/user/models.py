from django.db import models
# Create your models here.


class Models:
    class BaseUserData(models.Model):
        id = models.AutoField(primary_key=True)
        user = models.ForeignKey(
            'auths.UserProfile',
            on_delete=models.CASCADE,
            unique=False,
        )

        class Meta:
            abstract = True
            app_label = 'user'

    class BaseSetting(models.Model):
        user = models.OneToOneField(
            'auths.UserProfile',
            on_delete=models.CASCADE,
            unique=True,
        )

        class Meta:
            abstract = True
            app_label = 'user'

    class UserSet(BaseSetting):
        name = models.CharField(max_length=50)
        birthday = models.DateField(null=True)
        height = models.FloatField(null=True)
        gender = models.BooleanField(default=True)
        fcm_id = models.CharField(max_length=100)
        address = models.CharField(max_length=100)
        weight = models.CharField(max_length=10)
        phone = models.CharField(max_length=20)
        email = models.EmailField()
        default = models.OneToOneField(
            'user.Default',
            on_delete=models.SET_NULL,
            blank=True,
            null=True,
        )
        setting = models.OneToOneField(
            'user.Setting',
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
