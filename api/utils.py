import random
from functools import wraps

from django.utils import timezone
from django.forms.models import model_to_dict
from django.contrib.sessions.models import Session
from rest_framework import status, serializers
from rest_framework.response import Response

from api import logger
from api.models import BaseUser

from .auths.models import UserProfile


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
    def same_password(username: str) -> Response:
        logger.error(
            f"reset password failed: why do you reset password to the same one: {username}"
        )
        return Response(
            {"status": 1, "message": "fail"}, status=status.HTTP_401_UNAUTHORIZED
        )

    @staticmethod
    def user_is_not_active(username: str) -> Response:
        logger.error(f"login failed: user {username} is not active")
        return Response(
            {"status": 1, "message": "fail"}, status=status.HTTP_401_UNAUTHORIZED
        )

    @staticmethod
    def user_is_already_verified(username: str) -> Response:
        logger.warning(f"login failed: user {username} is already verified")
        return Response(
            {"status": 1, "message": "fail"}, status=status.HTTP_409_CONFLICT
        )

    @staticmethod
    def user_is_not_verified(username: str) -> Response:
        logger.warning(f"login failed: user {username} is not verified")
        return Response(
            {"status": 2, "message": "email not verified"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    @staticmethod
    def verification_code_is_wrong(username: str) -> Response:
        logger.error(f"login failed: verification code is wrong: {username}")
        return Response(
            {"status": 1, "message": "fail"}, status=status.HTTP_401_UNAUTHORIZED
        )

    @staticmethod
    def user_settings_does_not_exists(username: str) -> Response:
        logger.error(f"login failed: user settings does not exists: {username}")
        return Response(
            {"status": 1, "message": "fail"}, status=status.HTTP_401_UNAUTHORIZED
        )

    @staticmethod
    def invalid_datatype() -> Response:
        logger.error(f"invalid data type")
        return Response(
            {"status": 1, "message": "fail"}, status=status.HTTP_400_BAD_REQUEST
        )

    @staticmethod
    def relation_not_exists() -> Response:
        logger.error(f"relation not exists")
        return Response(
            {"status": 1, "message": "fail"}, status=status.HTTP_404_NOT_FOUND
        )

    @staticmethod
    def cannot_add_self() -> Response:
        logger.error(f"cannot add user self")
        return Response(
            {"status": 1, "message": "fail"}, status=status.HTTP_400_BAD_REQUEST
        )

    @staticmethod
    def already_answered() -> Response:
        logger.error(f"already answered this request")
        return Response(
            {"status": 1, "message": "fail"}, status=status.HTTP_409_CONFLICT
        )


def get_token_from_headers(request) -> str:
    """
    Extracts the bearer token from the request headers.

    Args:
        request: The request object.

    Returns:
        The bearer token as a string.

    Raises:
        AssertionError: If the bearer token is not found or is invalid.
    """
    bearer_token = request.headers.get("Authorization", "")

    # make sure the token is in header and is a bearer token
    assert bearer_token.startswith("Bearer "), "Bearer token not found or invalid"
    return bearer_token.split(" ")[1]


def get_user_by_token(
    token_key: str, allow_forgot_password: bool = False
) -> UserProfile:
    """
    Retrieve a user profile by token key.

    Args:
        token_key (str): The token key to retrieve the user profile.
        allow_forgot_password (bool, optional): Whether to allow retrieval of user profile with forgot password status. Defaults to False.

    Returns:
        UserProfile: The user profile associated with the token key.

    Raises:
        Session.DoesNotExist: If the session with the token key does not exist.
        UserProfile.DoesNotExist: If the user profile associated with the token key does not exist or is not active or has forgot password status and allow_forgot_password is False.
    """
    token = Session.objects.get(session_key=token_key)

    # check if token is expired
    if token.expire_date < timezone.now():
        logger.warning("Token expired")
        raise Session.DoesNotExist("Token expired")
    user = UserProfile.objects.get(id=token.get_decoded()["user_id"])

    if user.is_active is False:
        logger.warning("User not verified")
        raise UserProfile.DoesNotExist("User not verified")

    if user.is_forgot_password and not allow_forgot_password:
        logger.warning("Since user forgot it's password, we cannot get user by token")
        raise UserProfile.DoesNotExist("User forgot password")

    return user


def get_user_via_bearer(allow_forgot_password=False):
    """
    A decorator function that retrieves a user object from a bearer token in the request headers.

    Args:
        allow_forgot_password (bool): A flag indicating whether to allow users who forgot their password to authenticate.

    Returns:
        A decorated function that takes in an instance, request, user, and additional arguments and returns the result of the decorated function.
    """

    def inner(view_func):
        @wraps(view_func)
        def _wrapper_view(instance, request, *args, **kwargs) -> Response:
            """
            A decorator function that wraps a view function and adds authentication and authorization checks.

            Args:
                instance: The instance of the view function.
                request: The HTTP request object.
                *args: Additional positional arguments for the view function.
                **kwargs: Additional keyword arguments for the view function.

            Returns:
                The response object returned by the view function.
            """
            try:
                token = get_token_from_headers(request)
            except AssertionError as invalid_header:
                logger.error(invalid_header)
                return Response(
                    {"status": 1, "message": "fail"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            try:
                user = get_user_by_token(token, allow_forgot_password)
            except (Session.DoesNotExist, UserProfile.DoesNotExist):
                logger.error(
                    f"""failed to get user by token. this may be caused by:
                    1. token expired
                    2. user is not verified
                    3. user forgot password
                    """
                )
                return Response(
                    {"status": 1, "message": "fail"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            else:
                return view_func(instance, request, user, *args, **kwargs)

        return _wrapper_view

    return inner


get_user = get_user_via_bearer()


def random_username(k: int = 8) -> str:
    return f"User{''.join(random.choices('0123456789', k=k))}"
