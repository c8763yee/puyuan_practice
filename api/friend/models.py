from django.db import models

from api.models import BaseFriend
from puyuan.const import INVALID_FRIEND_TYPE, NOT_ANSWERED

from ..auths.models import UserProfile


# Create your models here.


class FriendSend(BaseFriend):
    relation = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="friend_relation"
    )
    type = models.IntegerField(default=INVALID_FRIEND_TYPE)
    status = models.IntegerField(default=NOT_ANSWERED)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
