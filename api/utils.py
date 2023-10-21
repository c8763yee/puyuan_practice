import json
import random
from functools import wraps

from django.utils import timezone
from django.contrib.sessions.models import Session
from rest_framework import status, serializers
from rest_framework.response import Response

from api import logger
from puyuan.const import ALNUM

from .auths.models import UserProfile


def failed_response(status: int = status.HTTP_400_BAD_REQUEST, **extra):
    return Response({"status": "1", "message": "fail", **extra}, status=status)


def warning_response(status: int, message: str, **extra):
    return Response({"status": "2", "message": message, **extra}, status=status)


class WarningResponse:
    """
    A class that contains static methods for generating warning responses with appropriate status codes and error messages.
    this is not that impacful to the system
    """

    @staticmethod
    def already_been_friends(user_name: str, friend_name: str) -> Response:
        """
        Returns a Response object with status code 409 (Conflict) and a message indicating that the users are already friends.

        Returns:
            Response: A Response object with status code 409 and a message indicating that the users are already friends.
        """
        logger.warning(
            f"add friend failed: {user_name} and {friend_name} have already been friends"
        )
        return warning_response(status.HTTP_409_CONFLICT, "already been friends")

    @staticmethod
    def user_is_not_verified(username: str) -> Response:
        """
        Returns a Response object with status code 401 (Unauthorized) and a message indicating that the user is not verified.

        Args:
            username (str): The username of the user that failed to log in.

        Returns:
            Response: A Response object with status code 401 and a message indicating that the user is not verified.
        """
        logger.warning(f"login failed: user {username} is not verified")
        return warning_response(
            message="email not verified",
            status=status.HTTP_401_UNAUTHORIZED,
        )


class FailedResponse:
    """
    A class that contains static methods for generating failed responses with appropriate status codes and error messages.
    """

    @staticmethod
    def friend_request_not_exists() -> Response:
        """
        Returns a Response object with status code 404 (Not Found) and a message indicating that the friend request does not exist.

        Returns:
            Response: A Response object with status code 404 and a message indicating that the friend request does not exist.
        """
        logger.error(f"this friend request does not exist")
        return failed_response(status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def cannot_get_token() -> Response:
        """
        Returns a Response object with status code 401 (Unauthorized) and a message indicating that the user cannot get a token.

        Returns:
            Response: A Response object with status code 401 and a message indicating that the user cannot get a token.
        """
        logger.error(f"cannot get token, please login again")
        return failed_response(status=status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    def invalid_date_format(date, expect_format: str) -> Response:
        logger.error(
            f"""invalid date:
                the valid date format is {expect_format} but got {date}
            """
        )
        return failed_response(status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def invalid_data(received_data: list[str], required: list[str]) -> Response:
        """
        Returns a Response object with status code 400 (Bad Request) and a message indicating that the data is invalid.

        Args:
            forms (list[str]): A list of form fields that were submitted.
            required (list[str]): A list of required form fields.

        Returns:
            Response: A Response object with status code 400 and a message indicating that the data is invalid.
        """
        logger.error(
            f""" Invalid data
            received: {received_data}
            required: {required}
            missing: {set(required) - set(received_data)}
            """
        )
        return failed_response(status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def serializer_is_not_valid(serializer: serializers.ModelSerializer) -> Response:
        """
        Returns a Response object with status code 400 (Bad Request) and a message indicating that the serializer is not valid.

        Args:
            serializer (serializers.ModelSerializer): A ModelSerializer instance that failed validation.

        Returns:
            Response: A Response object with status code 400 and a message indicating that the serializer is not valid.
        """
        logger.error(f"serializer is not valid, the error is: {serializer.errors}")
        return failed_response(status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def user_does_not_exists() -> Response:
        """
        Returns a Response object with status code 204 (No Content) and a message indicating that the user does not exist.

        Returns:
            Response: A Response object with status code 204 and a message indicating that the user does not exist.
        """
        logger.error(f"register failed: user not exists\n")
        return failed_response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def object_does_not_exists(object_name: str = "object") -> Response:
        """
        Returns a Response object with status code 204 (No Content) and a message indicating that the object does not exist.

        Args:
            object_name (str, optional): The name of the object that does not exist. Defaults to "object".

        Returns:
            Response: A Response object with status code 204 and a message indicating that the object does not exist.
        """
        logger.error(f"{object_name} not exists\n")
        return failed_response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def user_already_exists(email: str) -> Response:
        """
        Returns a Response object with status code 409 (Conflict) and a message indicating that the user already exists.

        Args:
            email (str): The email address of the user that already exists.

        Returns:
            Response: A Response object with status code 409 and a message indicating that the user already exists.
        """
        logger.error(f"register failed: user: {email} already exists")
        return failed_response(status=status.HTTP_409_CONFLICT)

    @staticmethod
    def password_is_wrong(username: str) -> Response:
        """
        Returns a Response object with status code 401 (Unauthorized) and a message indicating that the password is wrong.

        Args:
            username (str): The username of the user that failed to log in.

        Returns:
            Response: A Response object with status code 401 and a message indicating that the password is wrong.
        """
        logger.error(f"login failed: password is wrong: {username}")
        return failed_response(status=status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    def same_password(username: str) -> Response:
        """
        Returns a Response object with status code 401 (Unauthorized) and a message indicating that the new password is the same as the old one.

        Args:
            username (str): The username of the user that failed to reset their password.

        Returns:
            Response: A Response object with status code 401 and a message indicating that the new password is the same as the old one.
        """
        logger.error(
            f"reset password failed: why do you reset password to the same one: {username}"
        )
        return failed_response(status=status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    def user_is_not_active(username: str) -> Response:
        """
        Returns a Response object with status code 401 (Unauthorized) and a message indicating that the user is not active.

        Args:
            username (str): The username of the user that failed to log in.

        Returns:
            Response: A Response object with status code 401 and a message indicating that the user is not active.
        """
        logger.error(f"login failed: user {username} is not active")
        return failed_response(status=status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    def user_is_already_verified(username: str) -> Response:
        """
        Returns a Response object with status code 409 (Conflict) and a message indicating that the user is already verified.

        Args:
            username (str): The username of the user that failed to log in.

        Returns:
            Response: A Response object with status code 409 and a message indicating that the user is already verified.
        """
        logger.warning(f"login failed: user {username} is already verified")
        return failed_response(status=status.HTTP_409_CONFLICT)

    @staticmethod
    def verification_code_is_wrong(username: str) -> Response:
        """
        Returns a Response object with status code 401 (Unauthorized) and a message indicating that the verification code is wrong.

        Args:
            username (str): The username of the user that failed to log in.

        Returns:
            Response: A Response object with status code 401 and a message indicating that the verification code is wrong.
        """
        logger.error(f"login failed: verification code is wrong: {username}")
        return failed_response(status=status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    def user_settings_does_not_exists(username: str) -> Response:
        """
        Returns a Response object with status code 401 (Unauthorized) and a message indicating that the user settings do not exist.

        Args:
            username (str): The username of the user that failed to log in.

        Returns:
            Response: A Response object with status code 401 and a message indicating that the user settings do not exist.
        """
        logger.error(f"login failed: user settings does not exists: {username}")
        return failed_response(status=status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    def invalid_datatype() -> Response:
        """
        Returns a Response object with status code 400 (Bad Request) and a message indicating that the data type is invalid.

        Returns:
            Response: A Response object with status code 400 and a message indicating that the data type is invalid.
        """
        logger.error(f"invalid data type")
        return failed_response(status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def relation_not_exists() -> Response:
        """
        Returns a Response object with status code 404 (Not Found) and a message indicating that the relation does not exist.

        Returns:
            Response: A Response object with status code 404 and a message indicating that the relation does not exist.
        """
        logger.error(f"relation not exists")
        return failed_response(status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def cannot_add_self() -> Response:
        """
        Returns a Response object with status code 400 (Bad Request) and a message indicating that a user cannot add themselves.

        Returns:
            Response: A Response object with status code 400 and a message indicating that a user cannot add themselves.
        """
        logger.error(f"cannot add user self")
        return failed_response(status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def already_answered() -> Response:
        """
        Returns a Response object with status code 409 (Conflict) and a message indicating that the request has already been answered.

        Returns:
            Response: A Response object with status code 409 and a message indicating that the request has already been answered.
        """
        logger.error(f"already answered this request")
        return failed_response(status=status.HTTP_409_CONFLICT)

    @staticmethod
    def invalid_invite_code(invite_code: str) -> Response:
        """
        Returns a Response object with status code 404 (Not Found) and a message indicating that the invite code is invalid.

        Returns:
            Response: A Response object with status code 404 and a message indicating that the invite code is invalid.
        """
        logger.error(f"invalid invite code: {invite_code}")
        return failed_response(status=status.HTTP_404_NOT_FOUND)


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


def get_user_by_token(token_key: str) -> UserProfile:
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
    try:
        token = Session.objects.get(session_key=token_key)
    except Session.DoesNotExist:
        logger.warning("Token not found")
        raise Session.DoesNotExist("Token not found")

    if token.expire_date < timezone.now():
        logger.warning("Token expired")
        raise Session.DoesNotExist("Token expired")

    try:
        user = UserProfile.objects.get(id=token.get_decoded()["user_id"])
    except UserProfile.DoesNotExist:
        logger.warning("User not found")
        raise UserProfile.DoesNotExist("User not found")

    if user.is_active is False:
        logger.warning("User is not verified")
        raise UserProfile.DoesNotExist("User is not verified")

    return user


def get_userprofile(view_func):
    """
    A decorator function that wraps a view function and adds authentication and authorization checks.

    Args:
        allow_forgot_password (bool): A flag indicating whether to allow users who forgot their password to authenticate.

    Returns:
        A decorated function that takes in an instance, request, user, and additional arguments and returns the result of the decorated function.
    """

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
            user = get_user_by_token(token)
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


def random_username(k: int = 8, prefix="User") -> str:
    return f"{prefix}{''.join(random.choices(ALNUM, k=k))}"


def debug_request_data(data: dict):
    logger.debug(
        json.dumps(
            data,
            indent=4,
            ensure_ascii=False,
        )
    )
