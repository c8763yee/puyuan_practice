# Generated by Django 4.2.6 on 2023-10-11 14:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auths", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Default",
            fields=[
                (
                    "user_id",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("sugar_delta_max", models.FloatField(default=10.0)),
                ("sugar_delta_min", models.FloatField(default=1.0)),
                ("sugar_morning_max", models.FloatField(default=10.0)),
                ("sugar_morning_min", models.FloatField(default=1.0)),
                ("sugar_evening_max", models.FloatField(default=10.0)),
                ("sugar_evening_min", models.FloatField(default=1.0)),
                ("sugar_before_max", models.FloatField(default=10.0)),
                ("sugar_before_min", models.FloatField(default=1.0)),
                ("sugar_after_max", models.FloatField(default=10.0)),
                ("sugar_after_min", models.FloatField(default=1.0)),
                ("systolic_max", models.IntegerField(default=10)),
                ("systolic_min", models.IntegerField(default=1)),
                ("diastolic_max", models.IntegerField(default=10)),
                ("diastolic_min", models.IntegerField(default=1)),
                ("pulse_max", models.IntegerField(default=10)),
                ("pulse_min", models.IntegerField(default=1)),
                ("weight_max", models.FloatField(default=10.0)),
                ("weight_min", models.FloatField(default=1.0)),
                ("bmi_max", models.FloatField(default=10.0)),
                ("bmi_min", models.FloatField(default=1.0)),
                ("body_fat_max", models.FloatField(default=10.0)),
                ("body_fat_min", models.FloatField(default=1.0)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Setting",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("after_recoding", models.BooleanField()),
                ("no_recording_for_a_day", models.BooleanField()),
                ("over_max_or_under_min", models.BooleanField()),
                ("after_meal", models.BooleanField()),
                ("unit_of_sugar", models.BooleanField()),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="UserSet",
            fields=[
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("name", models.CharField(max_length=50)),
                ("birthday", models.DateField()),
                ("height", models.FloatField()),
                ("gender", models.BooleanField()),
                ("fcm_id", models.CharField(max_length=100)),
                ("address", models.CharField(max_length=100)),
                ("weight", models.CharField(max_length=10)),
                ("phone", models.CharField(max_length=20)),
                ("email", models.EmailField(max_length=254)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
