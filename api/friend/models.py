from django.db import models

from api.models import BaseFriend

from ..auths.models import UserProfile
from ..user.models import UserSet


# Create your models here.


class Relation(BaseFriend):
    invite_code = models.CharField(max_length=255, null=True)
    relation = models.ForeignKey(UserSet, on_delete=models.CASCADE, null=True)  # friend
    type = models.IntegerField(null=True)
    status = models.IntegerField(default=0)
    read = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
