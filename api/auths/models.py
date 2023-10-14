from django.db import models

from api.models import BaseUser

# Create your models here.


class UserProfile(BaseUser):
    is_forgot_password = models.BooleanField(default=False)
    login_time = models.IntegerField(default=0)

    USERNAME_FIELD = "id"
    REQUIRED_FIELDS = ["email", "username"]


class VerificationCode(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)


class News(models.Model):
    member_id = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    group = models.IntegerField()
    title = models.CharField(max_length=100)
    message = models.CharField(max_length=1000)
    pushed_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserRecord(models.Model):
    UID = models.AutoField(primary_key=True, unique=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, unique=False)
    id = models.IntegerField()
    type = models.IntegerField()
    relation_type = models.IntegerField()
