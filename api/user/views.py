import re
from typing import Type
from django.shortcuts import render
from django.forms.models import model_to_dict
from django.utils import timezone
from django.db.models import Model as django_model
from rest_framework import status, viewsets
from rest_framework.response import Response
from api import logger
from api.utils import get_user, FailedResponse

from puyuan.const import DEFAULT_DIARY_DICT

from . import serializer as SerializerModule, metadata as UserMetadata, models as Models

# Create your views here.


class UserInfo(viewsets.ViewSet):  # API No. 11 and 12
    metadata_class = UserMetadata.User
    serializer_class = SerializerModule.UserSetSerializer

    @get_user
    def list(self, request, user):  # method: GET
        user_set, created = Models.UserSet.objects.get_or_create(user=user)
        if created and user_set.default and user_set.setting:
            pass
        default = Models.Default.objects.get_or_create(user=user)[0]
        setting = Models.Setting.objects.get_or_create(user=user)[0]
        user_set.default = default
        user_set.setting = setting
        user_set.save()

        serializer_data = self.serializer_class(user_set).data
        return Response(
            {"status": 0, "message": "success", "user": serializer_data},
            status=status.HTTP_200_OK,
        )

    @get_user
    def partial_update(self, request, user, pk=None):
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid() is False:
            return FailedResponse.serializer_is_not_valid(serializer)

        try:
            instance = Models.UserSet.objects.get(user=user)
        except Models.UserSet.DoesNotExist:
            default = Models.Default.objects.get_or_create(user=user)[0]
            setting = Models.Setting.objects.get_or_create(user=user)[0]
            serializer.save(default=default, setting=setting, user_alt=user)
        else:
            serializer.update(instance, serializer.validated_data)

        if (email := request.data.get("email")) and user.email != email:
            user.email = email
            user.save()
        return Response({"status": 0, "message": "success"}, status=status.HTTP_200_OK)


class Default(viewsets.ViewSet):
    metadata_class = UserMetadata.Default
    serializer_class = SerializerModule.DefaultSerializer

    @get_user
    def partial_update(self, request, user, pk=None):
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid() is False:
            return FailedResponse.serializer_is_not_valid(serializer)

        if Models.Default.objects.filter(user=user).exists():
            instance = Models.Default.objects.get(user=user)
            serializer.update(instance, serializer.validated_data)
        else:
            serializer.save(user=user)

        return Response({"status": 0, "message": "success"}, status=status.HTTP_200_OK)


class Setting(viewsets.ViewSet):
    metadata_class = UserMetadata.Setting
    serializer_class = SerializerModule.SettingSerializer

    @get_user
    def partial_update(self, request, user, pk=None):
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid() is False:
            return FailedResponse.serializer_is_not_valid(serializer)
        if Models.Setting.objects.filter(user=user).exists():
            instance = Models.Setting.objects.get(user=user)
            serializer.update(instance, serializer.validated_data)
        else:
            serializer.save(user=user)

        return Response({"status": 0, "message": "success"}, status=status.HTTP_200_OK)


class BloodPressure(viewsets.ViewSet):
    metadata_class = UserMetadata.BloodPressure
    serializer_class = SerializerModule.BloodPressureSerializer

    @get_user
    def create(self, request, user):
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid() is False:
            return FailedResponse.serializer_is_not_valid(serializer)
        serializer.save(user=user)
        return Response({"status": 0, "message": "success"}, status=status.HTTP_200_OK)


class Weight(viewsets.ViewSet):
    metadata_class = UserMetadata.Weight
    serializer_class = SerializerModule.WeightSerializer

    @get_user
    def create(self, request, user):
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid() is False:
            return FailedResponse.serializer_is_not_valid(serializer)
        serializer.save(user=user, recorded_at=timezone.now())
        return Response({"status": 0, "message": "success"}, status=status.HTTP_200_OK)


class BloodSugar(viewsets.ViewSet):
    metadata_class = UserMetadata.BloodSugar
    serializer_class = SerializerModule.BloodSugarSerializer

    @get_user
    def create(self, request, user):
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid() is False:
            return FailedResponse.serializer_is_not_valid(serializer)
        serializer.save(user=user, recorded_at=timezone.now())
        return Response({"status": 0, "message": "success"}, status=status.HTTP_200_OK)


class Record(viewsets.ViewSet):  # API No.18 and 21
    metadata_class = UserMetadata.Record

    @get_user
    def create(self, request, user):
        try:
            diets = request.data["diets"]
        except KeyError:
            return FailedResponse.invalid_data(request.data.keys(), ["diets"])

        blood_pressure = Models.BloodPressure.objects.filter(user=user).last()
        weight = Models.Weight.objects.filter(user=user).last()
        blood_sugar = Models.BloodSugar.objects.filter(
            user=user, timeperiod=diets
        ).last()

        blood_sugar_value = (
            model_to_dict(blood_sugar, fields=["sugar"]) if blood_sugar else {}
        )

        blood_pressure_value = (
            model_to_dict(blood_pressure, fields=["systolic", "diastolic", "pulse"])
            if blood_pressure
            else {}
        )

        weight_value = model_to_dict(weight, fields=["weight"]) if weight else {}

        return Response(
            {
                "status": 0,
                "message": "success",
                "blood_sugars": blood_sugar_value,
                "blood_pressures": blood_pressure_value,
                "weights": weight_value,
            }
        )

    @get_user
    def destroy(self, request, user, pk=None):
        blood_pressure_to_delete = request.data.get("blood_pressure", [])
        weight_to_delete = request.data.get("weights", [])
        blood_sugar_to_delete = request.data.get("blood_sugars", [])

        if any(
            isinstance(to_delete, list) is False
            for to_delete in [
                blood_pressure_to_delete,
                weight_to_delete,
                blood_sugar_to_delete,
            ]
        ):
            return FailedResponse.invalid_datatype()

        Models.BloodPressure.objects.filter(
            user=user, id__in=blood_pressure_to_delete
        ).delete()
        Models.Weight.objects.filter(user=user, id__in=weight_to_delete).delete()
        Models.BloodSugar.objects.filter(
            user=user, id__in=blood_sugar_to_delete
        ).delete()

        return Response({"status": 0, "message": "success"}, status=status.HTTP_200_OK)


class Diary(viewsets.ViewSet):
    metadata_class = UserMetadata.Diary

    @get_user
    def list(self, request, user):
        return_data = []
        self.idx = 0

        def add_data(
            model: Type[django_model],
            data_type: str,
            fields: list[str] = [
                "user"
            ],  # use user as default because every model has user field
            exclude: list[str] = [],
            extra_arguments: dict[str, list[str]] = {},
        ):
            instances = model.objects.filter(user=user).all()
            for instance in instances:
                source_dict = DEFAULT_DIARY_DICT.copy()
                instance_dict = (
                    model_to_dict(instance, fields=fields)
                    if exclude == []
                    else model_to_dict(instance, exclude=exclude)
                )

                for extra_field, extra_field_value in extra_arguments.items():
                    instance_dict[extra_field] = {
                        value: attr
                        for value in extra_field_value
                        if (attr := getattr(instance, value, None))
                        and attr not in instance_dict.keys()
                    }

                source_dict.update(
                    user_id=user.id,
                    type=data_type,
                    **instance_dict,
                )
                source_dict["id"] = self.idx
                self.idx += 1
                return_data.append(source_dict)

        try:
            date_time = request.query_params["date"]
        except KeyError:
            return FailedResponse.invalid_data(request.query_params.keys(), ["date"])

        if re.match(r"^\d{4}-\d{2}-\d{2}$", date_time) is None:
            return FailedResponse.invalid_date_format(date_time, "%Y-%m-%d")

        # we only check startswith for getting data since the recorded_at is timezone.now()
        # and we only need to check the date(YYYY-MM-DD)

        add_data(Models.BloodPressure, "blood_pressure", exclude=["user"])
        add_data(Models.BloodSugar, "blood_sugar", exclude=["user"])
        add_data(
            Models.Diet,
            "diet",
            exclude=["user", "lat", "lng", "tag", "image"],
            extra_arguments={
                "location": ["lat", "lng"],
                "tags": ["name", "message"],
            },
        )
        add_data(Models.Weight, "weight", exclude=["user"])

        return Response({"status": 0, "message": "success", "diaries": return_data})


class Diet(viewsets.ViewSet):
    metadata_class = UserMetadata.Diet
    serializer_class = SerializerModule.DietSerializer

    @get_user
    def create(self, request, user):
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid() is False:
            return FailedResponse.serializer_is_not_valid(serializer)

        serializer.save(user=user)
        return Response({"status": 0, "message": "success"})


class A1c(viewsets.ViewSet):
    metadata_class = UserMetadata.A1c
    serializer_class = SerializerModule.A1cSerializer

    @get_user
    def list(self, request, user):
        serializer = self.serializer_class(
            Models.A1c.objects.filter(user=user), many=True
        )
        return Response({"status": 0, "message": "success", "a1c": serializer.data})

    @get_user
    def create(self, request, user):
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid() is False:
            return FailedResponse.serializer_is_not_valid(serializer)

        serializer.save(user=user)
        return Response({"status": 0, "message": "success"})

    @get_user
    def destroy(self, request, user, pk=None):
        ids = request.data.get("ids", [])
        if isinstance(ids, list) is False:
            return FailedResponse.invalid_datatype()

        Models.A1c.objects.filter(user=user, id__in=ids).delete()
        return Response({"status": 0, "message": "success"}, status=status.HTTP_200_OK)


class Medical(viewsets.ViewSet):
    metadata_class = UserMetadata.Medical
    serializer_class = SerializerModule.MedicalSerializer

    @get_user
    def list(self, request, user):
        medical_info = {}
        medical = Models.Medical.objects.filter(user=user).first()
        if medical is None:
            medical = Models.Medical.objects.create(user=user)
        medical_info = model_to_dict(medical)
        # manually add created_at and updated_at because model_to_dict won't include them
        medical_info["created_at"] = medical.created_at
        medical_info["updated_at"] = medical.updated_at
        medical_info["user_id"] = medical_info.pop("user")

        return Response({"status": 0, "message": "success", "medical": medical_info})

    @get_user
    def partial_update(self, request, user, pk=None):
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid() is False:
            return FailedResponse.serializer_is_not_valid(serializer)
        if Models.Medical.objects.filter(user=user).exists():
            instance = Models.Medical.objects.get(user=user)
            serializer.update(instance, serializer.validated_data)
        else:
            serializer.save(user=user)
        return Response({"status": 0, "message": "success"}, status=status.HTTP_200_OK)


class Drug(viewsets.ViewSet):
    metadata_class = UserMetadata.Drug
    serializer_class = SerializerModule.DrugSerializer

    @get_user
    def list(self, request, user):
        serializer = self.serializer_class(
            Models.Drug.objects.filter(user=user), many=True
        )
        return Response(
            {"status": 0, "message": "success", "drug_useds": serializer.data}
        )

    @get_user
    def create(self, request, user):
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid() is False:
            return FailedResponse.serializer_is_not_valid(serializer)

        serializer.save(user=user)
        return Response({"status": 0, "message": "success"})

    @get_user
    def destroy(self, request, user, pk=None):
        ids = request.data.get("ids", [])
        if isinstance(ids, list) is False:
            return FailedResponse.invalid_datatype()

        Models.Drug.objects.filter(user=user, id__in=ids).delete()
        return Response({"status": 0, "message": "success"}, status=status.HTTP_200_OK)


class Care(viewsets.ViewSet):
    metadata_class = UserMetadata.Care
    serializer_class = SerializerModule.CareSerializer

    @get_user
    def list(self, request, user):
        serializer = self.serializer_class(
            Models.Care.objects.filter(user=user), many=True
        )
        if serializer.data:
            return Response(
                {"status": 0, "message": "success", "cares": serializer.data}
            )
        return Response({"status": 0, "message": "success", "cares": []})

    @get_user
    def create(self, request, user):
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid() is False:
            return FailedResponse.serializer_is_not_valid(serializer)
        serializer.save(user=user, reply_id=1)
        return Response({"status": 0, "message": "success"})


class Badge(viewsets.ViewSet):
    @get_user
    def update(self, request, user):  # method: PUT
        pass
