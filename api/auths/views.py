import random

from django.shortcuts import render
from django.utils import timezone
from rest_framework import serializers, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response


from api import logger
from api.serializers import create_serializer
from api.utils import FailedResponse, get_user_via_bearer, random_username

from . import metadata as AuthMetadata
from .models import News, UserProfile, UserRecord, VerificationCode

# Create your views here.
DAY = 60 * 60 * 24


class Register(viewsets.ViewSet):
    metadata_class = AuthMetadata.Register

    def create(self, request):
        try:
            email = request.data["email"]
            password = request.data["password"]
        except KeyError:
            return FailedResponse.invalid_data(
                request.data.keys(), ["email", "password"]
            )
        user, created = UserProfile.objects.get_or_create(email=email)

        if created is False:
            return FailedResponse.user_already_exists(email)
        else:
            user.username = random_username()
        user.set_password(password)

        user.save()
        return Response(
            {"status": 0, "message": "success"}, status=status.HTTP_201_CREATED
        )


class Login(viewsets.ViewSet):
    # convert above docstring into json schema
    metadata_class = AuthMetadata.Auth

    def create(self, request):
        email = request.data["email"]
        password = request.data["password"]
        try:
            user = UserProfile.objects.get(email=email)
        except UserProfile.DoesNotExist:
            return FailedResponse.user_does_not_exists()

        if user.check_password(password) is False:
            return FailedResponse.password_is_wrong(user.username)

        if user.is_active is False:
            return FailedResponse.user_is_not_active(user.username)

        user.is_forgot_password = False  # since user can login, we can see as user already reset password or remember password
        token, created = Token.objects.get_or_create(user=user)
        if (
            created is False
        ):  # if token already exists, delete old token and create new token
            Token.objects.filter(user=user).all().delete()
            token = Token.objects.create(user=user)

        Token.created = timezone.now()
        return Response(
            {"status": 0, "token": token.key, "message": "success"},
            status=status.HTTP_200_OK,
        )


class SendVerification(viewsets.ViewSet):
    metadata_class = AuthMetadata.SendVerification

    def create(self, request):
        email = request.data["email"]
        try:
            user = UserProfile.objects.get(email=email)
        except UserProfile.DoesNotExist:
            return FailedResponse.user_does_not_exists()

        if user.is_active:
            return FailedResponse.user_already_verified(email)

        if VerificationCode.objects.filter(user_id=user.id).exists():  # type: ignore
            VerificationCode.objects.filter(user_id=user.id).all().delete()  # type: ignore

        verification_code = VerificationCode.objects.create(user_id=user.id)  # type: ignore
        verification_code.code = f"{random.randint(0, 100000):05d}"
        logger.info(f"verification code: {verification_code.code}")
        verification_code.save()
        return Response({"status": 0, "message": "success"}, status=status.HTTP_200_OK)


class CheckVerification(viewsets.ViewSet):
    metadata_class = AuthMetadata.CheckVerification

    def create(self, request):
        email = request.data["email"]
        code = request.data["code"]
        try:
            user = UserProfile.objects.get(email=email)
        except UserProfile.DoesNotExist:
            return FailedResponse.user_does_not_exists()
        if user.is_active:
            return FailedResponse.user_already_exists(email)

        try:
            verification_code = VerificationCode.objects.get(user_id=user.id)  # type: ignore
        except VerificationCode.DoesNotExist:
            return Response({"status": 1, "message": "fail"}, status=status.HTTP_200_OK)

        if verification_code.code != code:
            return Response({"status": 1, "message": "fail"}, status=status.HTTP_200_OK)

        user.is_active = True
        user.save()
        verification_code.delete()
        return Response({"status": 0, "message": "success"}, status=status.HTTP_200_OK)


class ForgotPassword(viewsets.ViewSet):
    metadata_class = AuthMetadata.ForgotPassword

    def create(self, request):
        email = request.data["email"]
        try:
            user = UserProfile.objects.get(email=email)
        except UserProfile.DoesNotExist:
            return FailedResponse.user_does_not_exists()
        else:
            user.is_forgot_password = True
            user.save()
            logger.debug(f"token: {user.generate_token()}")
            return Response(
                {"status": 0, "message": "success"}, status=status.HTTP_200_OK
            )


class ResetPassword(viewsets.ViewSet):
    metadata_class = AuthMetadata.ResetPassword

    @get_user_via_bearer
    def create(self, request, user):
        password = request.data["password"]
        user.set_password(password)
        user.is_forgot_password = False
        user.save()
        Token.objects.filter(user=user).all().delete()
        return Response({"status": 0, "message": "success"}, status=status.HTTP_200_OK)


class CheckRegister(viewsets.ViewSet):
    metadata_class = AuthMetadata.CheckRegister

    def list(self, request):
        email = request.GET.get("email")
        if not email:  # return failed if email is None or empty
            return Response(
                {"status": 1, "message": "fail"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            UserProfile.objects.get(email=email)
        except UserProfile.DoesNotExist:
            return Response({"status": 1, "message": "fail"}, status=status.HTTP_200_OK)
        return Response({"status": 0, "message": "success"}, status=status.HTTP_200_OK)


class NewsView(viewsets.ViewSet):
    metadata_class = AuthMetadata.News
    serializers_class = create_serializer(
        News, apply_ro_fields=["user", "created_at", "updated_at", "pushed_at"]
    )

    @get_user_via_bearer
    def list(self, request, user):
        News.objects.create(
            member_id=user, group=1, title="test", message="test"
        ).save()

        read_serializer = self.serializers_class(
            News.objects.filter(member_id=user), many=True
        )
        return Response(
            {"status": 0, "message": "success", "news": read_serializer.data}
        )


class Share(viewsets.ViewSet):
    metadata_class = AuthMetadata.Share
    serializer_class = create_serializer(
        UserRecord, apply_fields=["id", "type", "relation_type"]
    )

    @get_user_via_bearer
    def create(self, request, user):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError:
            return FailedResponse.serializer_is_not_valid(serializer)
        else:
            serializer.save(user_id=user.id)
            return Response(
                {"status": 0, "message": "success"}, status=status.HTTP_200_OK
            )


class CheckShare(viewsets.ViewSet):
    metadata_class = AuthMetadata.CheckShare
    serializer_class = create_serializer(UserRecord)

    @get_user_via_bearer
    def list(self, request, user, Type):
        records = UserRecord.objects.filter(user_id=user.id, relation_type=int(Type))

        serialization_records = self.serializer_class(records, many=True).data

        # delete user field for all records in serializer.data
        for record in serialization_records:
            del record["user"]
            del record["UID"]

        return Response(
            {"status": 0, "message": "success", "records": serialization_records}
        )
