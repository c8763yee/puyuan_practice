import random
from datetime import timedelta
from functools import wraps
import stat

from django.utils import timezone
from django.forms.models import model_to_dict
from rest_framework import status, serializers
from rest_framework.response import Response

from api import logger
from api.models import BaseUser
from puyuan.const import TOKEN_EXPIRE_TIME

from .auths.models import UserProfile, Token


class FailedResponse:
    @staticmethod
    def invalid_data(forms: list[str], required: list[str]) -> Response:
        logger.error(
            f""" Invalid data
            forms: {forms}
            required: {required}
            missing: {set(required) - set(forms)}
            """
        )
        return Response(
            {"status": 1, "message": "fail"}, status=status.HTTP_400_BAD_REQUEST
        )

    @staticmethod
    def serializer_is_not_valid(serializer: serializers.ModelSerializer) -> Response:
        logger.error(f"serializer is not valid: {serializer.errors}")
        return Response(
            {"status": 1, "message": "fail"}, status=status.HTTP_400_BAD_REQUEST
        )

    @staticmethod
    def user_does_not_exists() -> Response:
        logger.error(f"register failed: user not exist")
        return Response(
            {"status": 1, "message": "fail"}, status=status.HTTP_204_NO_CONTENT
        )

    @staticmethod
    def user_already_exists(email: str) -> Response:
        logger.error(f"register failed: user: {email} already exists")
        return Response(
            {"status": 1, "message": "fail"}, status=status.HTTP_409_CONFLICT
        )

    @staticmethod
    def password_is_wrong(username: str) -> Response:
        logger.error(f"login failed: password is wrong: {username}")
        return Response(
            {"status": 1, "message": "fail"}, status=status.HTTP_401_UNAUTHORIZED
        )

    @staticmethod
    def user_is_not_active(username: str) -> Response:
        logger.error(f"login failed: user is not active: {username}")
        return Response(
            {"status": 1, "message": "fail"}, status=status.HTTP_401_UNAUTHORIZED
        )

    @staticmethod
    def user_already_verified(username: str) -> Response:
        logger.warning(f"login failed: user already verified: {username}")
        return Response(
            {"status": 1, "message": "fail"}, status=status.HTTP_409_CONFLICT
        )

    @staticmethod
    def user_not_verified(username: str) -> Response:
        logger.error(f"login failed: user not verified: {username}")
        return Response(
            {"status": 2, "message": "email not verified"},
            status=status.HTTP_401_UNAUTHORIZED,
        )


def get_token_from_headers(request) -> str:
    bearer_token = request.headers.get("Authorization", "")
    # make sure the token is in header and is a bearer token
    assert bearer_token.startswith("Bearer "), "Bearer token not found or invalid"
    return bearer_token.split(" ")[1]


def get_user_by_token(token_key) -> BaseUser:
    # it will raise DoesNotExist exception if token not found, and it will be caught in the caller function. so no need to check if token exists
    token = Token.objects.get(key=token_key)

    if timezone.now() - token.created > timedelta(seconds=TOKEN_EXPIRE_TIME):
        logger.warning("Token expired")
        token.delete()
        raise Token.DoesNotExist("Token expired")

    user = token.user
    if user.is_active is False:
        logger.warning("User not verified")
        raise UserProfile.DoesNotExist("User not verified")

    if user.is_forgot_password is True:
        logger.warning("Since user forgot it's password, we cannot get user by token")
        raise UserProfile.DoesNotExist("User forgot password")

    return user


def get_user_via_bearer(view_func):
    @wraps(view_func)
    def _wrapper_view(instance, request, *args, **kwargs):
        try:
            token = get_token_from_headers(request)
        except AssertionError as invalid_header:
            logger.error(invalid_header)
            return Response(
                {"status": 1, "message": "fail"}, status=status.HTTP_401_UNAUTHORIZED
            )
        try:
            user = get_user_by_token(token)
        except (Token.DoesNotExist, UserProfile.DoesNotExist):
            logger.error(
                f"""failed to get user by token. this may be caused by:
                1. token expired
                2. user is not verified
                3. user forgot password
                """
            )
            return Response(
                {"status": 1, "message": "fail"}, status=status.HTTP_401_UNAUTHORIZED
            )
        else:
            return view_func(instance, request, user, *args, **kwargs)

    return _wrapper_view


def random_username() -> str:
    return f"User{random.randint(0, 100000000):08d}"


def model_to_dict_without_user(model: UserProfile) -> dict:
    model_dict = model_to_dict(model)
    del model_dict["user"]
    return model_dict
