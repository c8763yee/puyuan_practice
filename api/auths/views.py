from enum import verify
import random

from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import serializers, status, viewsets
from rest_framework.response import Response

from puyuan.const import MINUTE, DAY, ALNUM
from puyuan.settings import EMAIL_HOST_USER

from api import logger
from api.utils import FailedResponse, get_userprofile, random_username, WarningResponse, log_json_data

from . import serializer as SerializerModule, models as Models

from ..user.models import Default, Setting, Medical

# Create your views here.


class Register(viewsets.ViewSet):
    serializer_class = SerializerModule.Register

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid() is False:
            return FailedResponse.serializer_is_not_valid(serializer)

        email = serializer.validated_data["email"]
        if Models.UserProfile.objects.filter(email=email).exists():
            return FailedResponse.user_already_exists(email)

        serializer.save(
            verified=False,
            username=random_username(),
            invite_code=str(random.randint(0, int(1e8))),
        )

        return Response({"status": "0", "message": "success"})


class Login(viewsets.ViewSet):
    # convert above docstring into json schema
    serializer_class = SerializerModule.Login

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid() is False:
            return FailedResponse.serializer_is_not_valid(serializer)
        try:
            user = Models.UserProfile.objects.get(
                email=serializer.validated_data["email"]
            )
        except Models.UserProfile.DoesNotExist:
            return FailedResponse.user_does_not_exists()

        if user.check_password(serializer.validated_data["password"]) is False:
            return FailedResponse.password_is_wrong(user.username)

        if user.verified is False:
            return WarningResponse.user_is_not_verified(user.username)

        if user.must_change_password is False:  # user is not forget password
            request.session.flush()
            request.session.set_expiry(DAY)

        request.session["user_id"] = user.id
        request.session.save()

        Default.objects.get_or_create(user=user)
        Setting.objects.get_or_create(user=user)
        Medical.objects.get_or_create(user=user)
        user.last_login = timezone.now()
        user.login_times += 1
        user.save()

        token = request.session.session_key
        return Response({"status": "0", "message": "success", "token": token})


class SendVerification(viewsets.ViewSet):
    def create(self, request):
        try:
            email = request.data["email"]
        except KeyError:
            return FailedResponse.invalid_data(request.data.keys(), ["email"])

        try:
            user = Models.UserProfile.objects.get(email=email)
        except Models.UserProfile.DoesNotExist:
            return FailedResponse.user_does_not_exists()

        if user.verified:
            return FailedResponse.user_is_already_verified(email)

        user.verification_code = f"{random.randint(0, 1000000):06d}"
        logger.info(f"verification code: {user.verification_code}")
        send_mail(
            "Verification Code",
            f"Your verification code are {user.verification_code}",
            EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        user.save()
        return Response(
            {"status": "0", "message": "success"}, status=status.HTTP_201_CREATED
        )


class CheckVerification(viewsets.ViewSet):
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

        if user.verified:
            return FailedResponse.user_is_already_verified(email)

        if user.verification_code != code:
            return FailedResponse.verification_code_is_wrong(user.username)

        user.verified = True
        user.verification_code = None
        user.save()
        return Response({"status": "0", "message": "success"})


class ForgotPassword(viewsets.ViewSet):
    def create(self, request):
        try:
            email = request.data["email"]
        except KeyError:
            return FailedResponse.invalid_data(request.data.keys(), ["email"])
        try:
            user = Models.UserProfile.objects.get(email=email)
        except Models.UserProfile.DoesNotExist:
            return FailedResponse.user_does_not_exists()

        request.session["user_id"] = user.id
        request.session.set_expiry(5 * MINUTE)
        request.session.save()

        temp_password = "".join(random.choices(ALNUM, k=8))

        send_mail(
            "Reset Password",
            f"""Please access this link to reset password: http://localhost:8000/password/reset
            your temporary password is {temp_password}
            """,
            EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        user.must_change_password = True
        user.set_password(temp_password)
        user.save()

        return Response(
            {"status": "0", "message": "success"}, status=status.HTTP_201_CREATED
        )


class ResetPassword(viewsets.ViewSet):
    @get_userprofile
    def create(self, request, user):
        try:
            reseted_password = request.data["password"]
        except KeyError:
            return FailedResponse.invalid_data(request.data.keys(), ["password"])

        user.must_change_password = False
        user.set_password(reseted_password)
        user.save()

        request.session.set_expiry(DAY)
        request.session.save()
        return Response({"status": "0", "message": "success"})


class CheckRegister(viewsets.ViewSet):
    def list(self, request):
        try:
            email = request.query_params["email"]
        except KeyError:
            return FailedResponse.invalid_data(request.query_params.keys(), ["email"])

        try:
            Models.UserProfile.objects.get(email=email)
        except Models.UserProfile.DoesNotExist:
            return Response({"status": "0", "message": "success"})

        return FailedResponse.user_already_exists(email)


class News(viewsets.ViewSet):
    @get_userprofile  # type: ignore
    def list(self, request, user):
        return Response({"status": "0", "message": "success", "news": []})


class Share(viewsets.ViewSet):
    serializer_class = SerializerModule.Share

    @get_userprofile
    def create(self, request, user):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError:
            return FailedResponse.serializer_is_not_valid(serializer)
        else:
            serializer.save(user=user)
            return Response({"status": "0", "message": "success"})


class CheckShare(viewsets.ViewSet):
    # serializer_class = SerializerModule.CheckShare

    @get_userprofile
    def list(self, request, user, Type):
        # records = Models.UserRecord.objects.filter(user=user, relation_type=int(Type))

        # serialization_records = self.serializer_class(records, many=True).data
        # log_json_data(serialization_records, prefix="CheckShare")
        return Response(
            {"status": "0", "message": "success", "records": []}
        )
