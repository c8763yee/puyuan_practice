import random

from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import serializers, status, viewsets
from rest_framework.response import Response

from puyuan.const import MINUTE, DAY
from puyuan.settings import EMAIL_HOST_USER

from api import logger
from api.utils import (
    FailedResponse,
    get_user_via_bearer,
    random_username,
    WarningResponse,
)

from . import metadata as AuthMetadata, serializer as SerializerModule, models as Models

# Create your views here.


class Register(viewsets.ViewSet):
    metadata_class = AuthMetadata.Register
    serializer_class = SerializerModule.Register

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid() is False:
            return FailedResponse.serializer_is_not_valid(serializer)

        email = serializer.validated_data["email"]
        if Models.UserProfile.objects.filter(email=email).exists():
            return FailedResponse.user_already_exists(email)

        serializer.save(is_active=False, username=random_username())
        return Response(
            {"status": 0, "message": "success"}, status=status.HTTP_201_CREATED
        )


class Login(viewsets.ViewSet):
    # convert above docstring into json schema
    metadata_class = AuthMetadata.Auth
    serializer_class = SerializerModule.Login

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid() is False:
            return FailedResponse.serializer_is_not_valid(serializer)

        user = Models.UserProfile.objects.get(email=request.data["email"])
        if user.check_password(serializer.validated_data["password"]) is False:
            return FailedResponse.password_is_wrong(user.username)

        if user.is_active is False:
            return WarningResponse.user_is_not_verified(user.username)

        request.session.flush()
        request.session["user_id"] = user.id
        request.session["forgot_password"] = False
        request.session.set_expiry(DAY)
        request.session.save()

        user.last_login = timezone.now()
        user.login_time += 1
        user.save()

        token = request.session.session_key
        return Response(
            {"status": 0, "message": "success", "token": token},
            status=status.HTTP_200_OK,
        )


class SendVerification(viewsets.ViewSet):
    metadata_class = AuthMetadata.SendVerification

    def create(self, request):
        email = request.data["email"]
        try:
            user = Models.UserProfile.objects.get(email=email)
        except Models.UserProfile.DoesNotExist:
            return FailedResponse.user_does_not_exists()

        if user.is_active:
            return FailedResponse.user_is_already_verified(email)

        if Models.VerificationCode.objects.filter(user_id=user.id).exists():  # type: ignore
            Models.VerificationCode.objects.filter(user_id=user.id).all().delete()  # type: ignore

        verification_code = Models.VerificationCode.objects.create(user_id=user.id)  # type: ignore
        verification_code.code = f"{random.randint(0, 100000):05d}"
        logger.info(f"verification code: {verification_code.code}")
        send_mail(
            "Verification Code",
            f"Your verification code is {verification_code.code}",
            EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        verification_code.save()
        return Response(
            {"status": 0, "message": "success"}, status=status.HTTP_201_CREATED
        )


class CheckVerification(viewsets.ViewSet):
    metadata_class = AuthMetadata.CheckVerification

    def create(self, request):
        try:
            email = request.data["email"]
            code = request.data["code"]
        except KeyError:
            return FailedResponse.invalid_data(request.data.keys(), ["email", "code"])

        try:
            user = Models.UserProfile.objects.get(email=email)
        except Models.UserProfile.DoesNotExist:
            return FailedResponse.user_does_not_exists()

        if user.is_active:
            return FailedResponse.user_is_already_verified(email)

        try:
            verification_code = Models.VerificationCode.objects.get(user_id=user)  # type: ignore
        except Models.VerificationCode.DoesNotExist:
            return FailedResponse.user_already_exists(email)

        if verification_code.code != code:
            return FailedResponse.verification_code_is_wrong(user.username)

        user.is_active = True
        user.save()
        verification_code.delete()
        return Response({"status": 0, "message": "success"}, status=status.HTTP_200_OK)


class ForgotPassword(viewsets.ViewSet):
    metadata_class = AuthMetadata.ForgotPassword

    def create(self, request):
        email = request.data["email"]
        try:
            user = Models.UserProfile.objects.get(email=email)
        except Models.UserProfile.DoesNotExist:
            return FailedResponse.user_does_not_exists()
        else:
            user.is_forgot_password = True
            user.save()
        request.session.flush()
        request.session["user_id"] = user.id
        request.session.set_expiry(5 * MINUTE)
        request.session.save()
        send_mail(
            "Reset Password",
            f"""Please access this link to reset password: http://localhost:8000/reset-password
            your token is {request.session.session_key}
            """,
            EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        return Response(
            {"status": 0, "message": "success"}, status=status.HTTP_201_CREATED
        )


class ResetPassword(viewsets.ViewSet):
    metadata_class = AuthMetadata.ResetPassword

    @get_user_via_bearer(allow_forgot_password=True)
    def create(self, request, user):
        try:
            password = request.data["password"]
        except KeyError:
            return FailedResponse.invalid_data(request.data.keys(), ["password"])

        if user.check_password(password):
            return FailedResponse.same_password(user.username)

        user.set_password(password)
        user.is_forgot_password = False
        user.save()
        request.session.flush()
        return Response({"status": 0, "message": "success"}, status=status.HTTP_200_OK)


class CheckRegister(viewsets.ViewSet):
    metadata_class = AuthMetadata.CheckRegister

    def list(self, request):
        try:
            email = request.query_params["email"]
        except KeyError:
            return FailedResponse.invalid_data(request.query_params.keys(), ["email"])
        try:
            Models.UserProfile.objects.get(email=email)
        except Models.UserProfile.DoesNotExist:
            return FailedResponse.user_does_not_exists()
        return Response({"status": 0, "message": "success"}, status=status.HTTP_200_OK)


class News(viewsets.ViewSet):
    metadata_class = AuthMetadata.News
    serializers_class = SerializerModule.News

    @get_user_via_bearer()  # type: ignore
    def list(self, request, user):
        Models.News.objects.create(
            member_id=user, group=1, title="test", message="test"
        ).save()

        read_serializer = self.serializers_class(
            Models.News.objects.filter(member_id=user), many=True
        )
        return Response(
            {"status": 0, "message": "success", "news": read_serializer.data}
        )


class Share(viewsets.ViewSet):
    metadata_class = AuthMetadata.Share
    serializer_class = SerializerModule.Share

    @get_user_via_bearer()
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
    serializer_class = SerializerModule.CheckShare

    @get_user_via_bearer()
    def list(self, request, user, Type):
        records = Models.UserRecord.objects.filter(
            user_id=user.id, relation_type=int(Type)
        )

        serialization_records = self.serializer_class(records, many=True).data

        return Response(
            {"status": 0, "message": "success", "records": serialization_records}
        )
