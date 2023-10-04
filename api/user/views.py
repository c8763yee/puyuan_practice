import random

from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from api.serializers import create_serializer

from .metadata import UserMetadata
from .models import User, VerificationCode
# Create your views here.
DAY = 60 * 60 * 24


class UserView:
    class Register(viewsets.ViewSet):
        serializer_class = create_serializer(
            User, apply_fields=['email', 'password', 'is_active'], apply_ro_fields=['is_active'])
        metadata_class = UserMetadata.Register

        def create(self, request):
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'status': 0, 'message': 'success'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'status': 1, 'message': 'fail'}, status=status.HTTP_400_BAD_REQUEST)

    class Auth(viewsets.ViewSet):
        # convert above docstring into json schema
        metadata_class = UserMetadata.Auth

        def create(self, request):
            try:
                user = User.objects.get(email=request.data['email'])
            except User.DoesNotExist:
                return Response({'status': 1, 'message': 'fail'}, status=status.HTTP_200_OK)
            else:
                if user.password != request.data['password']:
                    return Response({'status': 1, 'message': 'fail'}, status=status.HTTP_200_OK)

                if user.is_active is False:
                    return Response({'status': 2, 'message': 'email not verified'}, status=status.HTTP_200_OK)

                # store data into session and get it's key as token
                request.session.flush()
                request.session['user_id'] = user.ID
                request.session.set_expiry(DAY)
                request.session.save()

                # get token with session
                token = request.session.session_key
                return Response({'status': 0, 'token': token, 'message': 'success'}, status=status.HTTP_200_OK)

    class SendVerification(viewsets.ViewSet):
        metadata_class = UserMetadata.SendVerification

        def create(self, request):
            try:
                user = User.objects.get(email=request.data['email'])
            except User.DoesNotExist:
                return Response({'status': 1, 'message': 'fail'}, status=status.HTTP_200_OK)
            else:
                verification_code = VerificationCode.objects.create(
                    user_id=user.ID)
                verification_code.code = f'{random.randint(0, 1000000):06d}'
                verification_code.save()
                return Response({'status': 0, 'message': 'success'}, status=status.HTTP_200_OK)

    class CheckVerification(viewsets.ViewSet):
        metadata_class = UserMetadata.CheckVerification

        def create(self, request):
            try:
                user = User.objects.get(email=request.data['email'])
            except User.DoesNotExist:
                return Response({'status': 1, 'message': 'fail'}, status=status.HTTP_200_OK)
            try:
                verification_code = VerificationCode.objects.get(
                    user_id=user.ID)
            except VerificationCode.DoesNotExist:
                return Response({'status': 1, 'message': 'fail'}, status=status.HTTP_200_OK)

            if verification_code.code != request.data['code']:
                return Response({'status': 1, 'message': 'fail'}, status=status.HTTP_200_OK)
            user.is_active = True
            user.save()
            verification_code.delete()
            verification_code.save()
            return Response({'status': 0, 'message': 'success'}, status=status.HTTP_200_OK)

    class ForgotPassword(viewsets.ViewSet):
        metadata_class = UserMetadata.ForgotPassword

        def create(self, request):
            try:
                user = User.objects.get(email=request.data['email'])
            except User.DoesNotExist:
                return Response({'status': 1, 'message': 'fail'}, status=status.HTTP_200_OK)
            else:
                request.session['token'] = user.token
                return Response({'status': 0, 'message': 'success'}, status=status.HTTP_200_OK)

    class ResetPassword(viewsets.ViewSet):
        metadata_class = UserMetadata.ResetPassword

        def create(self, request):
            return Response(
                # TODO: implement this
            )

    class CheckRegister(viewsets.ViewSet):
        metadata_class = UserMetadata.CheckRegister

        def list(self, request):
            return Response(
                # TODO: implement this
            )
