from curses import keyname
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class BaseUser(AbstractUser):
    class Meta:
        abstract = True
        app_label = "auths"


class BaseUserData(models.Model):  # allow multiple data for one user
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        "auths.UserProfile",
        on_delete=models.CASCADE,
        unique=False,
    )

    class Meta:
        abstract = True
        app_label = "user"


class BaseSetting(models.Model):  # allow only one setting per user
    user = models.OneToOneField(
        "auths.UserProfile",
        on_delete=models.CASCADE,
        unique=True,
    )

    class Meta:
        abstract = True
        app_label = "user"


class BaseFriend(BaseUserData):
    class Meta:
        abstract = True
        app_label = "friend"


# just in case that if i can't use django.contrib.auth.models.Token
class Token(models.Model):
    key = models.CharField(max_length=40, primary_key=True)
    user = models.ForeignKey(
        "auths.UserProfile",
        related_name="auth_token",
        on_delete=models.CASCADE,
    )
    created = models.DateTimeField(auto_now_add=True)
    expire = models.DateTimeField()

    class Meta:
        abstract = True
