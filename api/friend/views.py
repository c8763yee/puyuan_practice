import re
from typing import Type
from django.shortcuts import render
from django.forms.models import model_to_dict
from django.utils import timezone
from django.db.models import Model as django_model
from rest_framework import status, viewsets
from rest_framework.response import Response

from api import logger
from api.utils import get_user, FailedResponse, random_username

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
            user=user, invite_code=random_username(k=5)
        )
        return Response(
            {"status": 0, "message": "success", "invite_code": relation.invite_code}
        )


class List(viewsets.ViewSet):
    metadata_class = FriendMetadata.List
    serializer_class = SerializerModule.ListSerializer

    @get_user
    def list(self, request, user):
        serialzer = self.serializer_class(
            Models.Relation.objects.filter(user=user), many=True
        )
        return Response({"status": 0, "message": "success", "data": serialzer.data})


class Requests(viewsets.ViewSet):
    metadata_class = FriendMetadata.Requests
    serializer_class = SerializerModule.RequestSerializer

    @get_user
    def list(self, request, user):
        serializer = self.serializer_class(
            Models.Relation.objects.filter(user=user, type__lt=INVALID_TYPE), many=True
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
        except Models.Relation.DoesNotExist:
            return FailedResponse.relation_not_exists()

        if relation.user == user:
            return FailedResponse.cannot_add_self()

        relation.type = relation_type
        relation.relation = user
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

        relation.relation, _ = UserSet.objects.get_or_create(id=user.id)
        relation.status = ACCEPT
        relation.read = 1
        relation.save()
        return Response({"status": 0, "status": "success"})


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
        return Response({"status": 0, "status": "success"})


class Remove(viewsets.ViewSet):
    metadata_class = FriendMetadata.Remove

    @get_user
    def destroy(self, request, user):
        if (ids := request.data.get("ids"), "") == "":
            return FailedResponse.invalid_data(request.data, ["ids"])
        Models.Relation.objects.filter(id__in=ids).delete()
        return Response({"status": 0, "message": "success"})


class Results(viewsets.ViewSet):
    metadata_class = FriendMetadata.Result
    serializer_class = SerializerModule.ResultSerializer

    @get_user
    def list(self, request, user):
        serializer = self.serializer_class(
            Models.Relation.objects.filter(relation=user), many=True
        )
        return Response({"status": 0, "message": "success", "data": serializer.data})
