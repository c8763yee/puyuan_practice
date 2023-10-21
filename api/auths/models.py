from django.db import models

from api.models import BaseUser

# Create your models here.


class UserProfile(BaseUser):
    name = models.CharField(max_length=20, null=True, blank=True, default="")
    phone = models.CharField(max_length=20, blank=True, default="")
    fb_id = models.CharField(max_length=20, default="未設置")
    status = models.CharField(max_length=20, default="VIP")
    group = models.IntegerField(default=0)
    birthday = models.CharField(max_length=20, null=True, blank=True, default="")
    init_height = models.FloatField(
        "height", default=0.0
    )  # 這裡的 height 會被當成 'init_height
    init_weight = models.FloatField("weight", default=0.0)
    gender = models.BooleanField(default=True)
    address = models.CharField(max_length=100)
    verified = models.BooleanField(default=False)
    fcm_id = models.CharField(max_length=100)
    login_times = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    badge = models.IntegerField(default=0)

    verification_code = models.CharField(max_length=6, null=True)
    must_change_password = models.BooleanField(default=False)
    invite_code = models.CharField(max_length=10, null=True)  # some kind of UID

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]
    friend = models.CharField(max_length=100, blank=True, default="")  # store list

    @property
    def account(self):
        return self.email


class UserRecord(models.Model):
    UID = models.AutoField(primary_key=True, unique=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, unique=False)
    id = models.IntegerField()
    type = models.IntegerField()
    relation_type = models.IntegerField()
