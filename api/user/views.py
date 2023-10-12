from django.shortcuts import render
from django.forms.models import model_to_dict
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.response import Response
from api import logger
from api.utils import get_user_via_bearer, FailedResponse

from puyuan.const import DIET_TIME, DIET_LEN, DIARY_DICT

from . import serializer as SerializerModule
from .metadata import UserMetadata
from .models import Models

# Create your views here.


def diet_to_str(diet: int) -> str:
    assert diet < DIET_LEN and diet >= 0
    return DIET_TIME[diet]


class UserViewSet:
    class UserInfo(viewsets.ViewSet):
        metadata_class = UserMetadata.User

        @get_user_via_bearer
        def list(self, request, user):  # method: GET
            try:
                user_set = Models.UserSet.objects.get(user=user)
            except Models.UserSet.DoesNotExist:
                return Response({'status': 1, 'message': 'user not found'})

            serializer_data = SerializerModule.UserSetSerializer(user_set).data
            return Response(serializer_data, status=status.HTTP_200_OK)

        @get_user_via_bearer
        def partial_update(self, request, user, pk=None):  # method: PATCH
            serializer = SerializerModule.UserSetSerializer(
                data=request.data, partial=True)
            if serializer.is_valid() is False:
                return FailedResponse.serializer_is_not_valid(serializer)

            try:
                instance = Models.UserSet.objects.get(user=user)
            except Models.UserSet.DoesNotExist:
                default = Models.Default.objects.get_or_create(user=user)[0]
                setting = Models.Setting.objects.get_or_create(user=user)[0]
                serializer.save(default=default,
                                setting=setting, user_alt=user)
            else:
                serializer.update(instance, serializer.validated_data)

            if (email := request.data.get('email')) and user.email != email:
                user.email = email
                user.save()
            return Response({'status': 0, 'message': 'success'}, status=status.HTTP_200_OK)

    class Default(viewsets.ViewSet):
        metadata_class = UserMetadata.Default
        serializer_class = SerializerModule.DefaultSerializer

        @get_user_via_bearer
        def partial_update(self, request, user, pk=None):
            serializer = self.serializer_class(data=request.data, partial=True)
            if serializer.is_valid() is False:
                return FailedResponse.serializer_is_not_valid(serializer)

            if Models.Default.objects.filter(user=user).exists():
                instance = Models.Default.objects.get(user=user)
                serializer.update(instance, serializer.validated_data)
            else:
                serializer.save(user=user)

            return Response({'status': 0, 'message': 'success'}, status=status.HTTP_200_OK)

    class Setting(viewsets.ViewSet):
        metadata_class = UserMetadata.Setting
        serializer_class = SerializerModule.SettingSerializer

        @get_user_via_bearer
        def partial_update(self, request, user, pk=None):
            serializer = self.serializer_class(data=request.data, partial=True)
            if serializer.is_valid() is False:
                return FailedResponse.serializer_is_not_valid(serializer)
            if Models.Setting.objects.filter(user=user).exists():
                instance = Models.Setting.objects.get(user=user)
                serializer.update(instance, serializer.validated_data)
            else:
                serializer.save(user=user)

            return Response({'status': 0, 'message': 'success'}, status=status.HTTP_200_OK)

    class BloodPressure(viewsets.ViewSet):
        metadata_class = UserMetadata.BloodPressure
        serializer_class = SerializerModule.BloodPressureSerializer

        @get_user_via_bearer
        def create(self, request, user):
            serializer = self.serializer_class(data=request.data, partial=True)
            if serializer.is_valid() is False:
                return FailedResponse.serializer_is_not_valid(serializer)
            serializer.save(user=user, recorded_at=timezone.now())
            return Response({'status': 0, 'message': 'success'}, status=status.HTTP_200_OK)

    class Weight(viewsets.ViewSet):
        metadata_class = UserMetadata.Weight
        serializer_class = SerializerModule.WeightSerializer

        @get_user_via_bearer
        def create(self, request, user):
            serializer = self.serializer_class(data=request.data, partial=True)
            if serializer.is_valid() is False:
                return FailedResponse.serializer_is_not_valid(serializer)
            serializer.save(user=user, recorded_at=timezone.now())
            return Response({'status': 0, 'message': 'success'}, status=status.HTTP_200_OK)

    class BloodSugar(viewsets.ViewSet):
        metadata_class = UserMetadata.BloodSugar
        serializer_class = SerializerModule.BloodSugarSerializer

        @get_user_via_bearer
        def create(self, request, user):
            serializer = self.serializer_class(data=request.data, partial=True)
            if serializer.is_valid() is False:
                return FailedResponse.serializer_is_not_valid(serializer)
            serializer.save(user=user, recorded_at=timezone.now())
            return Response({'status': 0, 'message': 'success'}, status=status.HTTP_200_OK)

    class Record(viewsets.ViewSet):
        metadata_class = UserMetadata.Record

        @get_user_via_bearer
        def create(self, request, user):
            if (diets := request.data.get('diets')) is None or diets >= DIET_LEN:
                logger.error('diets time period is not provided or invalid')
                return Response({'status': 1, 'message': 'fail'})

            blood_pressure = Models.BloodPressure.objects.filter(
                user=user).last()
            weight = Models.Weight.objects.filter(user=user).last()
            blood_sugar = Models.BloodSugar.objects.filter(
                user=user, timeperiod=diets).last()

            blood_sugar_value = model_to_dict(
                blood_sugar, fields=['sugar']
            )if blood_sugar else {}

            blood_pressure_value = model_to_dict(blood_pressure, fields=[
                'systolic', 'diastolic', 'pulse']
            ) if blood_pressure else {}

            weight_value = model_to_dict(
                weight, fields=['weight']) if weight else {}

            return Response(
                {
                    'status': 0,
                    'message': 'success',
                    'blood_sugars': blood_sugar_value,
                    'blood_pressures': blood_pressure_value,
                    'weights': weight_value,
                }
            )

        @get_user_via_bearer
        def destroy(self, request, user, pk=None):
            blood_pressure_to_delete = request.data.get('blood_pressure', [])
            weight_to_delete = request.data.get('weights', [])
            blood_sugar_to_delete = request.data.get('blood_sugars', [])

            if any(
                    isinstance(to_delete, list) is False
                    for to_delete in [
                        blood_pressure_to_delete, weight_to_delete, blood_sugar_to_delete]
            ):

                logger.error('invalid data type')
                return Response({'status': 1, 'message': 'fail'})

            Models.BloodPressure.objects.filter(
                user=user, id__in=blood_pressure_to_delete).delete()
            Models.Weight.objects.filter(
                user=user, id__in=weight_to_delete).delete()
            Models.BloodSugar.objects.filter(
                user=user, id__in=blood_sugar_to_delete).delete()

            return Response({'status': 0, 'message': 'success'}, status=status.HTTP_200_OK)

    class Diary(viewsets.ViewSet):
        metadata_class = UserMetadata.Diary

        @get_user_via_bearer
        def list(self, request, user):
            return_data = []
            date_time = request.query_params.get('date')
            if date_time is None:
                logger.error('date is not provided')
                return Response({'status': 1, 'message': 'fail'})

            weights = Models.Weight.objects.filter(
                recorded_at__startswith=date_time, user=user)
            blood_pressures = Models.BloodPressure.objects.filter(
                recorded_at__startswith=date_time, user=user)
            blood_sugars = Models.BloodSugar.objects.filter(
                recorded_at__startswith=date_time, user=user)
