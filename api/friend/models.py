from django.db import models

from api.models import BaseFriend
from puyuan.const import INVALID_TYPE

from ..user.models import UserSet


# Create your models here.


class Relation(BaseFriend):
    invite_code = models.CharField(max_length=255, null=True)
    relation = models.ForeignKey(UserSet, on_delete=models.CASCADE, null=True)
    type = models.IntegerField(default=INVALID_TYPE)
    status = models.IntegerField(default=0)
    read = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
