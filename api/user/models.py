from django.db import models

# Create your models here.


class BaseUser(models.Model):

    class Meta:
        abstract = True
        app_label = 'user'


class User(BaseUser):
    ID = models.AutoField(primary_key=True, auto_created=True)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)


class VerificationCode(BaseUser):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
