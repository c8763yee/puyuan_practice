from django.db import models
# Create your models here.


class Models:
    class BaseUserData(models.Model):
        UID = models.AutoField(primary_key=True)
        user = models.ForeignKey(
            'auths.UserProfile',
            on_delete=models.CASCADE,
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
        # user cannot have multiple user set
        name = models.CharField(max_length=50)
        birthday = models.DateField()
        height = models.FloatField()
        gender = models.BooleanField()
        fcm_id = models.CharField(max_length=100)
        address = models.CharField(max_length=100)
        weight = models.CharField(max_length=10)
        phone = models.CharField(max_length=20)
        email = models.EmailField()

    class Default(BaseSetting):
        sugar_delta_max = models.FloatField()
        sugar_delta_min = models.FloatField()
        sugar_morning_max = models.FloatField()
        sugar_morning_min = models.FloatField()
        sugar_evening_max = models.FloatField()
        sugar_evening_min = models.FloatField()
        sugar_before_max = models.FloatField()
        sugar_before_min = models.FloatField()
        sugar_after_max = models.FloatField()
        sugar_after_min = models.FloatField()
        systolic_max = models.IntegerField()
        systolic_min = models.IntegerField()
        diastolic_max = models.IntegerField()
        diastolic_min = models.IntegerField()
        pulse_max = models.IntegerField()
        pulse_min = models.IntegerField()
        weight_max = models.FloatField()
        weight_min = models.FloatField()
        bmi_max = models.FloatField()
        bmi_min = models.FloatField()
        body_fat_max = models.FloatField()
        body_fat_min = models.FloatField()

    class Setting(BaseSetting):
        after_recording = models.BooleanField()
        no_recording_for_a_day = models.BooleanField()
        over_max_or_under_min = models.BooleanField()
        after_meal = models.BooleanField()
        unit_of_sugar = models.BooleanField()
        unit_of_weight = models.BooleanField()
        unit_of_height = models.BooleanField()

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
