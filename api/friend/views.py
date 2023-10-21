import re
from typing import Type
from django.shortcuts import render
from django.forms.models import model_to_dict
from rest_framework import viewsets
from rest_framework.response import Response

from api.utils import get_userprofile, FailedResponse, WarningResponse

from puyuan.const import NOT_ANSWERED, ACCEPT, REFUSE, INVALID_FRIEND_TYPE


from . import models as Models


# Create your views here.


class Code(viewsets.ViewSet):
    @get_userprofile
    def list(self, requst, user):
        return Response(
            {"status": "0", "message": "success", "invite_code": user.invite_code}
        )


class List(viewsets.ViewSet):
    @get_userprofile
    def list(self, request, user):
        relation_list = []
        friend_set = set(map(int, user.friend.split(", "))) if user.friend else set()
        friends = Models.FriendSend.objects.filter(user=user, id__in=friend_set).all()

        for friend in friends:
            relation_list.append(
                {
                    "id": friend.relation.id,  # type: ignore
                    "username": friend.relation.username,
                    "account": friend.relation.account,
                }
            )

        return Response({"status": "0", "message": "success", "friends": relation_list})


class Requests(viewsets.ViewSet):
    @get_userprofile
    def list(self, request, user):
        request_list = []
        requests = Models.FriendSend.objects.filter(
            user=user, status=NOT_ANSWERED, type__lt=INVALID_FRIEND_TYPE
        ).all()

        for friend_request in requests:
            request_dict = model_to_dict(friend_request, exclude=["user", "relation"])

            # manully add user_id and user and relation_id to friend_dict
            request_dict["user_id"] = user.id
            request_dict["relation_id"] = friend_request.relation.id  # type: ignore
            request_dict["user"] = {
                "id": friend_request.relation.id,  # type: ignore
                "username": friend_request.relation.username,
                "account": friend_request.relation.account,
            }

            request_list.append(request_dict)

        return Response({"status": "0", "message": "success", "requests": request_list})


class Send(viewsets.ViewSet):
    @get_userprofile
    def create(self, request, user):
        try:
            relation_type = request.data["type"]
            invite_code = request.data["invite_code"]
        except KeyError:
            return FailedResponse.invalid_data(request.data, ["type", "invite_code"])

        try:
            friend = Models.UserProfile.objects.get(invite_code=invite_code)
        except Models.UserProfile.DoesNotExist:
            return FailedResponse.invalid_invite_code(invite_code)

        if friend.id == user.id:
            return FailedResponse.cannot_add_self()

        # check if the friend has already been added
        if friend.id in map(int, user.friends.split(", ")):
            return WarningResponse.already_been_friends(user.username, friend.username)

        Models.FriendSend.objects.create(user=user, relation=friend, type=relation_type)
        return Response({"status": "0", "message": "success"})


class Accept(viewsets.ViewSet):
    @get_userprofile
    def list(self, request, user, inviteid: int):
        try:
            friend_request = Models.FriendSend.objects.get(id=inviteid)
        except Models.FriendSend.DoesNotExist:
            return FailedResponse.friend_request_not_exists()

        if friend_request.status != NOT_ANSWERED:
            return FailedResponse.already_answered()

        friend_request.status = ACCEPT
        friend_request.read = True
        friend_request.save()

        # add friend to user's friend list
        user.friend = (
            user.friend
            + (", " if user.friend else "")
            + str(friend_request.relation.id)
        )
        user.save()
        return Response({"status": "0", "message": "success"})


class Refuse(viewsets.ViewSet):
    @get_userprofile
    def list(self, request, user, inviteid: int):
        try:
            friend_request = Models.FriendSend.objects.get(id=inviteid)
        except Models.FriendSend.DoesNotExist:
            return FailedResponse.friend_request_not_exists()

        if friend_request.status != NOT_ANSWERED:
            return FailedResponse.already_answered()

        friend_request.status = REFUSE
        friend_request.read = True
        friend_request.save()

        return Response({"status": "0", "message": "success"})


class Remove(viewsets.ViewSet):
    @get_userprofile
    def destroy(self, request, user):
        try:
            ids = request.data["ids"]
        except KeyError:
            return FailedResponse.invalid_data(request.data, ["ids"])

        friend_set = set(map(int, user.friend))

        Models.FriendSend.objects.filter(id__in=ids).delete()
        user.friend = ", ".join(friend_set.difference(set(ids)))
        user.save()
        return Response({"status": "0", "message": "success"})


class Result(viewsets.ViewSet):
    @get_userprofile
    def list(self, request, user):
        result_list = []
        results = Models.FriendSend.objects.filter(user=user, read=True).all()

        for result in results:
            result_dict = model_to_dict(result, exclude=["user", "relation"])

            # manully add user_id and user and relation_id to friend_dict
            result_dict["user_id"] = user.id
            result_dict["relation_id"] = result.relation.id  # type: ignore
            result_dict["relation"] = {
                "id": result.relation.id,
                "username": result.relation.username,
                "account": result.relation.account,
            }

            result_list.append(result_dict)

        return Response({"status": "0", "message": "success", "results": result_list})
