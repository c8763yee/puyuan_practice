from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.response import Response

from api import logger
from api.serializers import create_serializer
from api.utils import get_user_via_bearer, FailedResponse

from .metadata import UserMetadata
from .models import Models

from ..auths.models import UserProfile
# Create your views here.


class UserViewSet:
    class UserInfo(viewsets.ViewSet):
        metadata_class = UserMetadata.User
        serializer_class = create_serializer(Models.UserSet)

        @get_user_via_bearer
        def list(self, request, user):  # method: GET
            pass

        @get_user_via_bearer
        def partial_update(self, request, user, pk=None):  # method: PATCH
            # first serialize request data
            # then check if it is valid
            # then if user exists, update user info
            # then save

            serializer = self.serializer_class(data=request.data, partial=True)
            if serializer.is_valid() is False:
                return FailedResponse.serializer_is_not_valid(serializer)
            if Models.UserSet.objects.filter(user=user).exists():
                instance = Models.UserSet.objects.get(user=user)
                serializer.update(instance, serializer.validated_data)
            else:
                serializer.save(user=user)
            return Response({'status': 0, 'message': 'success'}, status=status.HTTP_200_OK)

    class Default(viewsets.ViewSet):
        metadata_class = UserMetadata.Default
        serializer_class = create_serializer(Models.Default)

        @get_user_via_bearer
        def partial_update(self, request, user, pk=None):
            serializer = self.serializer_class(data=request.data, partial=True)
            if serializer.is_valid() is False:
                return FailedResponse.serializer_is_not_valid(serializer)

            if Models.Default.objects.filter(user=user).exists():
                instance = Models.Default.objects.get(user=user)
                serializer.update(instance, serializer.validated_data)
            else:
                serializer.save(user=user)
            return Response({'status': 0, 'message': 'success'}, status=status.HTTP_200_OK)

    class Setting(viewsets.ViewSet):
        metadata_class = UserMetadata.Setting
        serializer_class = create_serializer(Models.Setting)

        @get_user_via_bearer
        def partial_update(self, request, user, pk=None):
            serializer = self.serializer_class(data=request.data, partial=True)
            if serializer.is_valid() is False:
                return FailedResponse.serializer_is_not_valid(serializer)
            if Models.Setting.objects.filter(user=user).exists():
                instance = Models.Setting.objects.get(user=user)
                serializer.update(instance, serializer.validated_data)
            else:
                serializer.save(user=user)
            return Response({'status': 0, 'message': 'success'}, status=status.HTTP_200_OK)

    class BloodPressure(viewsets.ViewSet):
        metadata_class = UserMetadata.BloodPressure
        serializer_class = create_serializer(Models.BloodPressure)

        @get_user_via_bearer
        def create(self, request, user, pk=None):
            serializer = self.serializer_class(data=request.data, partial=True)
            if serializer.is_valid() is False:
                return FailedResponse.serializer_is_not_valid(serializer)
            serializer.save(user=user)
            return Response({'status': 0, 'message': 'success'}, status=status.HTTP_200_OK)
