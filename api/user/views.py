from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.response import Response

from api.serializers import create_serializer
from api.auths.models import Auth

from .metadata import UserMetadata
from .models import UserProfile
# Create your views here.


class UserViewSet:
    class UserInfo(viewsets.ViewSet):
        metadata_class = UserMetadata.User
        serializer_class = create_serializer(UserProfile)

        def list(self, request):
            pass

        def partial_update(self, request, pk=None):  # method: PATCH
            bearer_token = request.META.get('HTTP_AUTHORIZATION')
            if bearer_token is None or bearer_token.startswith('Bearer ') is False:
                return Response({'status': 1, 'message': 'fail'}, status=status.HTTP_401_UNAUTHORIZED)
