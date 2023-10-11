import random
from functools import wraps

from django.forms.models import model_to_dict
from rest_framework import status, serializers
from rest_framework.response import Response

from api import logger

from .auths.models import UserProfile, Token


class FailedResponse:

    @staticmethod
    def user_does_not_exists() -> Response:
        logger.error(f"register failed: user not exist")
        return Response({'status': 1, 'message': 'fail'}, status=status.HTTP_200_OK)

    @staticmethod
    def user_already_exists(email: str) -> Response:
        logger.warning(f"register failed: user: {email} already exists")
        return Response({'status': 1, 'message': 'fail'}, status=status.HTTP_200_OK)

    @staticmethod
    def serializer_is_not_valid(serializer: serializers.ModelSerializer) -> Response:
        logger.error(f"serializer is not valid: {serializer.errors}")
        return Response({'status': 1, 'message': 'fail'}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def password_is_wrong(username: str) -> Response:
        logger.error(f"login failed: password is wrong: {username}")
        return Response({'status': 1, 'message': 'fail'}, status=status.HTTP_200_OK)

    @staticmethod
    def user_is_not_active(username: str) -> Response:
        logger.error(f"login failed: user is not active: {username}")
        return Response({'status': 1, 'message': 'fail'}, status=status.HTTP_200_OK)

    @staticmethod
    def user_already_verified(username: str) -> Response:
        logger.error(f"login failed: user already verified: {username}")
        return Response({'status': 1, 'message': 'fail'}, status=status.HTTP_200_OK)


def get_token(request) -> str:
    bearer_token = request.headers.get('Authorization', '')
    assert bearer_token.startswith('Bearer '), 'Bearer token not found'
    return bearer_token.split(' ')[1]


def get_user_via_bearer(view_func):
    @wraps(view_func)
    def _wrapper_view(instance, request, *args, **kwargs):
        try:
            token = get_token(request)
        except AssertionError as e:
            logger.error(e)
            return Response({'status': 1, 'message': 'fail'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            user = UserProfile.get_user_by_token(token)
        except (Token.DoesNotExist, UserProfile.DoesNotExist):
            return Response({'status': 1, 'message': 'fail'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return view_func(instance, request, user, *args, **kwargs)
    return _wrapper_view


def random_username() -> str:
    return f'User{random.randint(0, 100000000):08d}'


def model_to_dict_without_user(model: UserProfile) -> dict:
    model_dict = model_to_dict(model)
    del model_dict['user']
    return model_dict
