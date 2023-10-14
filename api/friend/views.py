import re
from typing import Type
from django.shortcuts import render
from django.forms.models import model_to_dict
from django.utils import timezone
from django.db.models import Model as django_model
from rest_framework import status, viewsets
from rest_framework.response import Response

from api import logger
from api.utils import get_user, FailedResponse, random_username, WarningResponse

from puyuan.const import NOT_ANSWERED, ACCEPT, REFUSE, INVALID_TYPE


from . import (
    serializer as SerializerModule,
    metadata as FriendMetadata,
    models as Models,
)

from ..user.models import UserSet

# Create your views here.


class Code(viewsets.ViewSet):
    metadata_class = FriendMetadata.Code

    @get_user
    def list(self, requst, user):
        relation = Models.Relation.objects.create(
            user=user, invite_code=random_username(k=5, prefix="")
        )
        return Response(
            {"status": 0, "message": "success", "invite_code": relation.invite_code}
        )


class List(viewsets.ViewSet):
    metadata_class = FriendMetadata.List

    @get_user
    def list(self, request, user):
        return_data = []
        relations = Models.Relation.objects.filter(user=user, type__lt=INVALID_TYPE)
        for relation in relations:
            related_user = relation.relation
            logger.info(model_to_dict(related_user))
            related_user_data = {
                "id": related_user.id,
                "name": related_user.name,
                "email": related_user.email,
            }
            return_data.append(related_user_data)
        return Response({"status": 0, "message": "success", "data": return_data})


class Requests(viewsets.ViewSet):
    metadata_class = FriendMetadata.Requests
    serializer_class = SerializerModule.RequestSerializer

    @get_user
    def list(self, request, user):
        serializer = self.serializer_class(
            Models.Relation.objects.filter(user=user, status=NOT_ANSWERED), many=True
        )
        return Response({"status": 0, "message": "success", "data": serializer.data})


class Send(viewsets.ViewSet):
    metadata_class = FriendMetadata.Send

    @get_user
    def create(self, request, user):
        try:
            relation_type = request.data["type"]
            invite_code = request.data["invite_code"]
        except KeyError:
            return FailedResponse.invalid_data(request.data, ["type", "invite_code"])

        try:
            relation = Models.Relation.objects.get(invite_code=invite_code)
            relation.relation = UserSet.objects.get(user=user)
        except (Models.Relation.DoesNotExist, UserSet.DoesNotExist):
            return FailedResponse.invalid_invite_code()

        if relation.user == user:
            return FailedResponse.cannot_add_self()

        if relation.status == ACCEPT:
            return WarningResponse.already_been_friends()

        relation.type = relation_type
        relation.save()
        return Response({"status": 0, "message": "success"})


class Accept(viewsets.ViewSet):
    metadata_class = FriendMetadata.Accept

    @get_user
    def list(self, request, user, inviteid):
        relation = Models.Relation.objects.get(id=inviteid)
        if relation is None:
            return FailedResponse.relation_not_exists()
        if relation.status != NOT_ANSWERED:
            return FailedResponse.already_answered()

        relation.relation = UserSet.objects.get(user=user)
        relation.status = ACCEPT
        relation.read = 1
        relation.save()
        return Response({"status": 0, "message": "success"})


class Refuse(viewsets.ViewSet):
    metadata_class = FriendMetadata.Refuse
    # serializer_class = SerializerModule.Refuse

    @get_user
    def list(self, request, user, inviteid):
        relation = Models.Relation.objects.get(id=inviteid)
        if relation is None:
            return FailedResponse.relation_not_exists()
        if relation.status != NOT_ANSWERED:
            return FailedResponse.already_answered()

        relation.relation = None
        relation.status = REFUSE
        relation.read = 1
        relation.save()
        return Response({"status": 0, "message": "success"})


class Remove(viewsets.ViewSet):
    metadata_class = FriendMetadata.Remove

    @get_user
    def destroy(self, request, user):
        if (ids := request.data.get("ids"), "") == "":
            return FailedResponse.invalid_data(request.data, ["ids"])
        Models.Relation.objects.filter(id__in=ids).delete()
        return Response({"status": 0, "message": "success"})


class Result(viewsets.ViewSet):
    metadata_class = FriendMetadata.Result
    serializer_class = SerializerModule.ResultSerializer

    @get_user
    def list(self, request, user):
        serializer = self.serializer_class(
            Models.Relation.objects.filter(user=user, type__lt=INVALID_TYPE, read=1),
            many=True,
        )
        return Response({"status": 0, "message": "success", "data": serializer.data})
