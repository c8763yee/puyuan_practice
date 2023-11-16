from django.shortcuts import render
from django.forms.models import model_to_dict
from rest_framework import viewsets
from rest_framework.response import Response

from api import logger
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
        friend_list = list(map(int, user.friend.split(", "))) if user.friend else []
        friends = Models.FriendSend.objects.filter(
            user=user, relation__id__in=friend_list
        ).all()

        for friend in friends:
            relation_list.append(
                {
                    "id": friend.relation.id,  # type: ignore
                    "name": friend.relation.username,
                    "relation_type": friend.type,
                }
            )
        return Response({"status": "0", "message": "success", "friends": relation_list})


class Requests(viewsets.ViewSet):
    @get_userprofile
    def list(self, request, user):  # me: user
        request_list = []
        requests = Models.FriendSend.objects.filter(
            relation=user, status=NOT_ANSWERED, read=False
        ).all()
        for friend_request in requests:
            request_dict = model_to_dict(friend_request, exclude=["user", "relation"])

            # manully add user_id and user and relation_id to friend_dict
            request_dict["user_id"] = user.id
            request_dict["relation_id"] = friend_request.relation.id  # type: ignore
            request_dict["user"] = {
                "id": friend_request.relation.id,  # type: ignore
                "name": friend_request.relation.username,
                "account": friend_request.relation.account,
            }
            request_dict["created_at"] = friend_request.created_at.strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            request_dict["updated_at"] = friend_request.updated_at.strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            # bool -> int
            request_dict["read"] = int(request_dict["read"])
            request_list.append(request_dict)
        print(request_list)
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
        if user.friend and friend.id in map(int, user.friend.split(", ")):
            return WarningResponse.already_been_friends(user.username, friend.username)

        request, created = Models.FriendSend.objects.get_or_create(
            user=user, relation=friend
        )
        if created is False:
            if request.status == ACCEPT:
                response = WarningResponse.already_been_friends(
                    user.username, friend.username
                )
            else:
                response = FailedResponse.already_sent_friend_request(
                    user.username, friend.username
                )
            request.delete()
            return response

        request.type = relation_type
        request.save()
        return Response({"status": "0", "message": "success"})


class Accept(viewsets.ViewSet):
    @get_userprofile
    # receive: relation
    # send: user
    def list(self, request, user, inviteid: int):
        try:
            friend_request = Models.FriendSend.objects.get(id=inviteid, relation=user)
        except Models.FriendSend.DoesNotExist:
            return FailedResponse.friend_request_not_exists()

        if friend_request.status != NOT_ANSWERED:
            return FailedResponse.already_answered()

        friend_request.status = ACCEPT
        friend_request.read = True
        friend_request.save()

        send = friend_request.user
        if send.friend:
            send.friend += ", "

        send.friend += str(user.id)
        send.save()

        if user.friend:
            user.friend += ", "
        user.friend += str(send.id)
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
            ids = request.data["ids[]"]
        except KeyError:
            return FailedResponse.invalid_data(request.data.keys(), ["ids[]"])

        if isinstance(ids, int):
            friend_set = {ids}
            ids_set = {ids}
        elif isinstance(ids, list):
            friend_set = set(map(int, user.friend))
            ids_set = set(ids)
        else:
            return FailedResponse.invalid_datatype()

        objects = Models.FriendSend.objects.filter(id__in=friend_set)
        objects.delete()

        user.friend = ", ".join(friend_set.difference(ids_set))
        user.save()
        friends_to_remove = Models.UserProfile.objects.filter(id__in=ids_set)
        for friend in friends_to_remove:
            relative_friend = friend.friend.split(", ")
            if str(user.id) not in relative_friend:
                continue

            relative_friend.remove(str(user.id))
            friend.friend = ", ".join(relative_friend)
            friend.save()

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
                "name": result.relation.username,
                "account": result.relation.account,
            }
            result_dict["read"] = int(result_dict["read"])
            result_dict["created_at"] = result.created_at.strftime("%Y-%m-%d %H:%M:%S")

            result_dict["updated_at"] = result.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            result_list.append(result_dict)

        return Response({"status": "0", "message": "success", "results": result_list})
