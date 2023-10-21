from functools import partial
import re
import json
from typing import Type

from django.shortcuts import render
from django.forms.models import model_to_dict
from django.db.models import Model as django_model
from rest_framework import viewsets
from rest_framework.response import Response

from api import logger
from api.utils import get_userprofile, FailedResponse

from puyuan.const import DEFAULT_DIARY_DICT, INVALID_DRUG_TYPE

from . import serializer as SerializerModule, models as Models

# Create your views here.


class UserInfo(viewsets.ViewSet):
    @get_userprofile
    def list(self, request, user):  # method: GET
        serializer_data = SerializerModule.UserSetOutputSerializer(user).data
        return Response(
            {"status": "0", "message": "success", "user": serializer_data},
        )

    @get_userprofile
    def partial_update(self, request, user, pk=None):
        name = request.data.get("name", None)
        birthday = request.data.get("birthday", None)
        height = request.data.get("height", None)
        weight = request.data.get("weight", None)
        phone = request.data.get("phone", None)
        email = request.data.get("email", None)
        gender = request.data.get("gender", None)
        fcm_id = request.data.get("fcm_id", None)
        address = request.data.get("address", None)

        for data in [
            "name",
            "birthday",
            "height",
            "weight",
            "phone",
            "email",
            "gender",
            "fcm_id",
            "address",
        ]:
            if not locals()[data]:
                continue

            if data == "height":
                user.init_height = locals()[data]
            elif data == "weight":
                user.init_weight = float(locals()[data])
            else:
                setattr(user, data, locals()[data])
        user.save()
        return Response(
            {"status": "0", "message": "success"},
        )


class Default(viewsets.ViewSet):
    serializer_class = SerializerModule.DefaultSerializer

    @get_userprofile
    def partial_update(self, request, user, pk=None):
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid() is False:
            return FailedResponse.serializer_is_not_valid(serializer)

        try:
            instance = Models.Default.objects.get(user=user)
        except Models.Default.DoesNotExist:
            serializer.save(user=user)
        else:
            serializer.update(instance, serializer.validated_data)

        return Response(
            {"status": "0", "message": "success"},
        )


class Setting(viewsets.ViewSet):
    serializer_class = SerializerModule.SettingSerializer

    @get_userprofile
    def partial_update(self, request, user, pk=None):
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid() is False:
            return FailedResponse.serializer_is_not_valid(serializer)

        try:
            instance = Models.Setting.objects.get(user=user)
        except Models.Setting.DoesNotExist:
            serializer.save(user=user)
        else:
            serializer.update(instance, serializer.validated_data)

        return Response(
            {"status": "0", "message": "success"},
        )


class BloodPressure(viewsets.ViewSet):
    serializer_class = SerializerModule.BloodPressureSerializer

    @get_userprofile
    def create(self, request, user):
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid() is False:
            return FailedResponse.serializer_is_not_valid(serializer)
        serializer.save(user=user)
        return Response(
            {"status": "0", "message": "success"},
        )


class Weight(viewsets.ViewSet):
    serializer_class = SerializerModule.WeightSerializer

    @get_userprofile
    def create(self, request, user):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid() is False:
            return FailedResponse.serializer_is_not_valid(serializer)
        serializer.save(user=user)
        user.weight = serializer.validated_data["weight"]  # type: ignore
        user.save()
        return Response(
            {"status": "0", "message": "success"},
        )


class BloodSugar(viewsets.ViewSet):
    serializer_class = SerializerModule.BloodSugarSerializer

    @get_userprofile
    def create(self, request, user):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid() is False:
            return FailedResponse.serializer_is_not_valid(serializer)
        serializer.save(user=user)
        return Response(
            {"status": "0", "message": "success"},
        )


class Record(viewsets.ViewSet):  # API No.18 and 21
    @get_userprofile
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
                "status": "0",
                "message": "success",
                "blood_sugars": blood_sugar_value,
                "blood_pressures": blood_pressure_value,
                "weights": weight_value,
            }
        )

    @get_userprofile
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

        return Response(
            {"status": "0", "message": "success"},
        )


class Diary(viewsets.ViewSet):
    @get_userprofile
    def list(self, request, user):
        return_data = []
        self.idx = 0

        def add_data(
            model: Type[django_model],
            data_type: str,
            fields: list[str] = [
                "user"
            ],  #  every model in this app must have user field
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
                        value: instance_attribute
                        for value in extra_field_value
                        if (instance_attribute := getattr(instance, value, None))
                        and instance_attribute not in instance_dict.keys()
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

        return Response({"status": "0", "message": "success", "diary": return_data})


class Diet(viewsets.ViewSet):
    serializer_class = SerializerModule.DietSerializer

    @get_userprofile
    def create(self, request, user):
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid() is False:
            return FailedResponse.serializer_is_not_valid(serializer)

        serializer.save(user=user)
        return Response({"status": "0", "message": "success"})


class A1c(viewsets.ViewSet):
    serializer_class = SerializerModule.A1cSerializer

    @get_userprofile
    def list(self, request, user):
        serializer = self.serializer_class(
            Models.A1c.objects.filter(user=user), many=True
        )
        return Response({"status": "0", "message": "success", "a1cs": serializer.data})

    @get_userprofile
    def create(self, request, user):
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid() is False:
            return FailedResponse.serializer_is_not_valid(serializer)

        serializer.save(user=user)
        return Response({"status": "0", "message": "success"})

    @get_userprofile
    def destroy(self, request, user, pk=None):
        ids = request.data.get("ids", [])
        if isinstance(ids, list) is False:
            return FailedResponse.invalid_datatype()

        Models.A1c.objects.filter(user=user, id__in=ids).delete()
        return Response(
            {"status": "0", "message": "success"},
        )


class Medical(viewsets.ViewSet):
    serializer_class = SerializerModule.MedicalSerializer

    @get_userprofile
    def list(self, request, user):
        medical_info = {}
        try:
            medical = Models.Medical.objects.get(user=user)
        except Models.Medical.DoesNotExist:
            return FailedResponse.object_does_not_exists(object_name="Medical")

        medical_info = model_to_dict(medical)
        # manually add created_at and updated_at because model_to_dict won't include them
        medical_info["created_at"] = medical.created_at
        medical_info["updated_at"] = medical.updated_at
        medical_info["user_id"] = medical_info.pop("user")

        # bool -> int
        medical_info["oad"] = int(medical_info["oad"])
        medical_info["insulin"] = int(medical_info["insulin"])
        medical_info["anti_hypertensives"] = int(medical_info["anti_hypertensives"])

        return Response(
            {"status": "0", "message": "success", "medical_info": medical_info}
        )

    @get_userprofile
    def partial_update(self, request, user, pk=None):
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid() is False:
            return FailedResponse.serializer_is_not_valid(serializer)
        try:
            instance = Models.Medical.objects.get(user=user)
        except Models.Medical.DoesNotExist:
            serializer.save(user=user)
        else:
            serializer.update(instance, serializer.validated_data)

        return Response(
            {"status": "0", "message": "success"},
        )


class Drug(viewsets.ViewSet):
    serializer_class = SerializerModule.DrugSerializer

    @get_userprofile
    def list(self, request, user):
        serializer = self.serializer_class(
            Models.Drug.objects.filter(user=user, type__lt=INVALID_DRUG_TYPE), many=True
        )
        return Response(
            {"status": "0", "message": "success", "drug_useds": serializer.data}
        )

    @get_userprofile
    def create(self, request, user):
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid() is False:
            return FailedResponse.serializer_is_not_valid(serializer)

        serializer.save(user=user)
        return Response({"status": "0", "message": "success"})

    @get_userprofile
    def destroy(self, request, user, pk=None):
        ids = request.data.get("ids", [])
        if isinstance(ids, list) is False:
            return FailedResponse.invalid_datatype()

        Models.Drug.objects.filter(user=user, id__in=ids).delete()
        return Response(
            {"status": "0", "message": "success"},
        )


class Care(viewsets.ViewSet):
    serializer_class = SerializerModule.CareSerializer

    @get_userprofile
    def list(self, request, user):
        serializer = self.serializer_class(
            Models.Care.objects.filter(user=user), many=True
        )

        return Response(
            {"status": "0", "message": "success", "cares": serializer.data or []}
        )

    @get_userprofile
    def create(self, request, user):
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid() is False:
            return FailedResponse.serializer_is_not_valid(serializer)
        serializer.save(user=user, reply_id=1)
        return Response({"status": "0", "message": "success"})


class Badge(viewsets.ViewSet):
    @get_userprofile
    def update(self, request, user):  # method: PUT
        badge = request.data.get("badge", -1)
        if isinstance(badge, int) and badge >= 0:
            user.badge = badge
            user.save()
        else:
            return FailedResponse.invalid_datatype()
        return Response({"status": "0", "message": "success"})
