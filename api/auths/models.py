from hashlib import md5, sha256

from django.db import models
from django.utils import timezone
from rest_framework.authtoken.models import Token

from api import logger
from api.models import BaseUser
from puyuan.const import SALT

# Create your models here.


def custom_hash(password):
    def md5_hash(word):
        return md5(word.encode()).hexdigest()

    def sha256_hash(word):
        return sha256(word.encode()).hexdigest()

    words = rf"{SALT}password{SALT}ok{sha256_hash(password+md5_hash(password))}{SALT}"
    return sha256_hash(words)


class UserProfile(BaseUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=20, unique=False)
    is_active = models.BooleanField(default=False)
    is_forgot_password = models.BooleanField(default=False)
    USERNAME_FIELD = "id"

    def generate_token(self) -> str:
        Token.objects.filter(user=self).delete()

        token = Token.objects.create(user=self, created=timezone.now())
        return token.key

    def set_password(self, raw_password):
        return super().set_password(custom_hash(raw_password))

    def check_password(self, raw_password):
        return super().check_password(custom_hash(raw_password))


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
