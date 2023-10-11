from datetime import timedelta
from hashlib import md5, sha256
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from rest_framework.authtoken.models import Token

from api import logger
from puyuan.const import SALT
# Create your models here.


MINUTE = 60
TOKEN_EXPIRE_TIME = 30 * MINUTE


def custom_hash(password):

    def md5_hash(word):
        return md5(word.encode()).hexdigest()

    def sha256_hash(word):
        return sha256(word.encode()).hexdigest()

    words = rf'{SALT}password{SALT}ok{sha256_hash(password+md5_hash(password))}{SALT}'
    return sha256_hash(words)


class BaseUser(AbstractUser):
    class Meta:
        abstract = True
        app_label = 'auths'


class Auth(BaseUser):
    ID = models.AutoField(primary_key=True, unique=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=20, unique=False)
    USERNAME_FIELD = 'ID'
    verified = models.BooleanField(default=False)

    def generate_token(self):
        Token.objects.filter(user=self).delete()

        token = Token.objects.create(
            user=self, created=timezone.now())
        return token.key

    def set_password(self, raw_password):
        return super().set_password(custom_hash(raw_password))

    def check_password(self, raw_password):
        return super().check_password(custom_hash(raw_password))

    @staticmethod
    def get_user_by_token(token_key):

        token = Token.objects.get(key=token_key)
        if timezone.now() - token.created > timedelta(minutes=TOKEN_EXPIRE_TIME):
            logger.info("Token expired")
            token.delete()
            return None
        return token.user


class VerificationCode(models.Model):
    user = models.ForeignKey(Auth, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
