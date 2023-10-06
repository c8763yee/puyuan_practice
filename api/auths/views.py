import random

from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.utils import timezone

from api import logger

from .metadata import AuthMetadata
from .models import Auth, VerificationCode
# Create your views here.
DAY = 60 * 60 * 24


def random_username():
    return f'User{random.randint(0, 1e8):08d}'


def user_does_not_exists(email):
    logger.error(f"register failed: user: {email} not exist")
    return Response({'status': 1, 'message': 'fail'}, status=status.HTTP_200_OK)


def serializer_is_not_valid(serializer):
    logger.error(f"register failed: {serializer.errors}")
    return Response({'status': 1, 'message': 'fail'}, status=status.HTTP_400_BAD_REQUEST)


class AuthView:
    class Register(viewsets.ViewSet):
        metadata_class = AuthMetadata.Register

        def create(self, request):
            email = request.data['email']
            password = request.data['password']
            user = Auth.objects.create(
                email=email, username=random_username())
            user.set_password(password)
            user.save()
            return Response({'status': 0, 'message': 'success'}, status=status.HTTP_201_CREATED)

    class Login(viewsets.ViewSet):
        # convert above docstring into json schema
        metadata_class = AuthMetadata.Auth

        def create(self, request):
            email = request.data['email']
            password = request.data['password']
            try:
                user = Auth.objects.get(email=email)
            except Auth.DoesNotExist:
                return user_does_not_exists(email)
            if user.check_password(password) is False:
                logger.error(
                    f"login failed: user: {email}")
                return Response({'status': 1, 'message': 'fail'}, status=status.HTTP_200_OK)
            if user.activated is False:
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
        metadata_class = AuthMetadata.SendVerification

        def create(self, request):
            email = request.data['email']
            try:
                user = Auth.objects.get(email=email)
            except Auth.DoesNotExist:
                return user_does_not_exists(email)
            if VerificationCode.objects.filter(user_id=user.ID).exists():
                VerificationCode.objects.filter(
                    user_id=user.ID).all().delete()
            verification_code = VerificationCode.objects.create(
                user_id=user.ID)
            verification_code.code = f'{random.randint(0, 100000):05d}'
            logger.info(f'verification code: {verification_code.code}')
            verification_code.save()
            return Response({'status': 0, 'message': 'success'}, status=status.HTTP_200_OK)

    class CheckVerification(viewsets.ViewSet):
        metadata_class = AuthMetadata.CheckVerification

        def create(self, request):
            email = request.data['email']
            code = request.data['code']
            try:
                user = Auth.objects.get(email=email)
            except Auth.DoesNotExist:
                return user_does_not_exists(email)
            try:
                verification_code = VerificationCode.objects.get(
                    user_id=user.ID)
            except VerificationCode.DoesNotExist:
                return Response({'status': 1, 'message': 'fail'}, status=status.HTTP_200_OK)
            if verification_code.code != code:
                return Response({'status': 1, 'message': 'fail'}, status=status.HTTP_200_OK)
            user.activated = True
            user.save()
            verification_code.delete()
            return Response({'status': 0, 'message': 'success'}, status=status.HTTP_200_OK)

    class ForgotPassword(viewsets.ViewSet):
        metadata_class = AuthMetadata.ForgotPassword

        def create(self, request):
            email = request.data['email']
            try:
                user = Auth.objects.get(email=email)
            except Auth.DoesNotExist:
                return user_does_not_exists(email)
            else:
                logger.debug(f'token: {user.generate_token()}')
                return Response({'status': 0, 'message': 'success'}, status=status.HTTP_200_OK)

    class ResetPassword(viewsets.ViewSet):
        metadata_class = AuthMetadata.ResetPassword

        def create(self, request):
            password = request.data['password']
            # get bearer token
            if (Authorization := request.headers.get('Authorization')) is None:
                return Response({'status': 1, 'message': 'fail'}, status=status.HTTP_200_OK)
            token = Authorization.split(' ')[1]  # bearer ${token}
            try:
                user = Auth.get_user_by_token(token)
            except Token.DoesNotExist:
                return Response({'status': 1, 'message': 'fail'}, status=status.HTTP_200_OK)
            user.set_password(password)
            user.save()
            Token.objects.filter(user=user).all().delete()
            return Response({'status': 0, 'message': 'success'}, status=status.HTTP_200_OK)

    class CheckRegister(viewsets.ViewSet):
        metadata_class = AuthMetadata.CheckRegister

        def list(self, request):
            email = request.GET.get('email')
            if not email:  # return failed if email is None or empty
                return Response({'status': 1, 'message': 'fail'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                Auth.objects.get(email=email)
            except Auth.DoesNotExist:
                return Response({'status': 1, 'message': 'fail'}, status=status.HTTP_200_OK)
            return Response({'status': 0, 'message': 'success'}, status=status.HTTP_200_OK)

    class News(viewsets.ViewSet):
        metadata_class = AuthMetadata.News

        def list(self, request):
            now = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            return Response(
                {
                    "status": 0,
                    "message": "success",
                    "news": [
                        {
                            "id": 1,
                            "member_id": 1,
                            "group": 1,
                            "title": "test",
                            "message": "test",
                            "pushed_at": now,
                            "created_at": now,
                            "updated_at": now
                        }
                    ]
                }
            )

    class Share(viewsets.ViewSet):
        metadata_class = AuthMetadata.Share

        def create(self, request):
            # TODO: get all data from id and store the data into database
            return Response({'status': 0, 'message': 'success'}, status=status.HTTP_200_OK)

    class CheckShare(viewsets.ViewSet):
        metadata_class = AuthMetadata.CheckShare

        def list(self, request, Type):
            # TODO: 根據指定的關係，回傳所有記錄的資料後，把所有資料個別整理成血壓、體重、血糖、減肥日記，用JSON格式回傳。
            """
            record:{
                "blood_pressure": {
                    "systolic": 120,
                    "diastolic": 80,
                },
                "weight": 50,
                "blood_sugar": 100,
                "diary": {
                    "date": "2021-08-29",
                    "content": "test"
                }                    
            }
            """
            return Response(
                {}
            )
