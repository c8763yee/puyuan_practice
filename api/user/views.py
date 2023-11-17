import re
import json
from typing import Type

from django.shortcuts import render
from django.forms.models import model_to_dict
from django.db.models import Model as django_model
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.response import Response

from api import logger
from api.utils import get_userprofile, FailedResponse, log_json_data

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

        for data_name in [
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
            if not locals()[data_name]:
                continue

            # Because of the different data type of height and weight, we need to store it as other name and type in database
            if data_name == "height":
                user.init_height = locals()[data_name]
            elif data_name == "weight":
                user.init_weight = float(locals()[data_name])
            else:
                setattr(user, data_name, locals()[data_name])
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
            diets = request.data["diet"]
        except KeyError:
            return FailedResponse.invalid_data(request.data.keys(), ["diet"])

        blood_pressure = Models.BloodPressure.objects.filter(user=user).last()
        weight = Models.Weight.objects.filter(user=user).last()
        blood_sugar = Models.BloodSugar.objects.filter(
            user=user, timeperiod=diets
        ).last()

        blood_sugar_value = (
            model_to_dict(blood_sugar, fields=["sugar"])
            if blood_sugar
            else {"sugar": 0.0}
        )

        blood_pressure_value = (
            model_to_dict(blood_pressure, fields=["systolic", "diastolic", "pulse"])
            if blood_pressure
            else {
                "systolic": 0,
                "diastolic": 0,
                "pulse": 0,
            }
        )

        weight_value = (
            model_to_dict(weight, fields=["weight"]) if weight else {"weight": 0.0}
        )

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
        try:
            delete_object = request.data["deleteObject"]
        except KeyError:
            return FailedResponse.invalid_data(request.data.keys(), ["deleteObject"])

        blood_pressure_to_delete: list = delete_object.get("blood_pressures", [])
        weight_to_delete = delete_object.get("weights", [])
        blood_sugar_to_delete = delete_object.get("blood_sugars", [])
        diets_to_delete = delete_object.get("diets", [])

        if any(
            isinstance(to_delete, list) is False
            for to_delete in [
                blood_pressure_to_delete,
                weight_to_delete,
                blood_sugar_to_delete,
                diets_to_delete,
            ]
        ):
            return FailedResponse.invalid_datatype()

        Models.BloodPressure.objects.filter(id__in=blood_pressure_to_delete).delete()
        Models.Weight.objects.filter(id__in=weight_to_delete).delete()
        Models.BloodSugar.objects.filter(id__in=blood_sugar_to_delete).delete()
        Models.Diet.objects.filter(id__in=diets_to_delete).delete()
        return Response(
            {"status": "0", "message": "success"},
        )


class Diary(viewsets.ViewSet):
    @get_userprofile
    def list(self, request, user):
        try:
            date_time = request.query_params["date"]
        except KeyError:
            return FailedResponse.invalid_data(request.query_params.keys(), ["date"])

        if re.match(r"^\d{4}-\d{2}-\d{2}$", date_time) is None:
            return FailedResponse.invalid_date_format(date_time, "%Y-%m-%d")
        return_data = []

        # --------------------- add data to return_data for each model ---------------------
        blood_pressure_data_all = Models.BloodPressure.objects.filter(
            user=user, recorded_at__startswith=date_time
        ).all()
        for blood_pressure_data in blood_pressure_data_all:
            source_dict = DEFAULT_DIARY_DICT.copy()
            source_dict.update(
                user_id=user.id,
                type="blood_pressure",
                **model_to_dict(blood_pressure_data, exclude=["user"]),
            )
            source_dict["id"] = blood_pressure_data.id

            return_data.append(source_dict)

        blood_sugar_data_all = Models.BloodSugar.objects.filter(
            user=user, recorded_at__startswith=date_time
        ).all()
        for blood_sugar_data in blood_sugar_data_all:
            source_dict = DEFAULT_DIARY_DICT.copy()
            source_dict.update(
                user_id=user.id,
                type="blood_sugar",
                **model_to_dict(blood_sugar_data, exclude=["user"]),
            )
            source_dict["id"] = blood_sugar_data.id

            return_data.append(source_dict)

        weight_data_all = Models.Weight.objects.filter(
            user=user, recorded_at__startswith=date_time
        ).all()
        for weight_data in weight_data_all:
            source_dict = DEFAULT_DIARY_DICT.copy()
            source_dict.update(
                user_id=user.id,
                type="weight",
                **model_to_dict(weight_data, exclude=["user"]),
            )
            source_dict["id"] = weight_data.id

            return_data.append(source_dict)

        diet_data_all = Models.Diet.objects.filter(
            user=user, recorded_at__startswith=date_time
        ).all()
        for diet_data in diet_data_all:
            source_dict = DEFAULT_DIARY_DICT.copy()
            source_dict.update(
                user_id=user.id,
                type="diet",
                **model_to_dict(
                    diet_data, exclude=["user", "lat", "lng", "tag", "image"]
                ),
                location={
                    "lat": str(diet_data.lat),
                    "lng": str(diet_data.lng),
                },
                tags={
                    "name": diet_data.tag.split(", "),
                    "message": "",
                },
            )
            source_dict["id"] = diet_data.id

            return_data.append(source_dict)

        # --------------------- END ---------------------
        log_json_data(return_data, prefix="Diary:")
        return Response({"status": "0", "message": "success", "diary": return_data})


class Diet(viewsets.ViewSet):
    serializer_class = SerializerModule.DietSerializer

    @get_userprofile
    def create(self, request, user):
        request.data["tag"] = request.data.pop("tag[]")
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid() is False:
            return FailedResponse.serializer_is_not_valid(serializer)

        serializer.save(user=user)
        return Response(
            {"status": "0", "message": "success", "image_url": "sdfkjfldakjsdfkl"}
        )


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
        try:
            a1c = request.data["a1c"]
            recorded_at = request.data["recorded_at"]
        except KeyError:
            return FailedResponse.invalid_data(
                request.data.keys(), ["a1c", "recorded_at"]
            )

        Models.A1c.objects.create(user=user, a1c=a1c, recorded_at=recorded_at)
        return Response({"status": "0", "message": "success"})

    @get_userprofile
    def destroy(self, request, user, pk=None):
        ids = request.data.get("ids[]", [])
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
        print(serializer.validated_data)
        serializer.save(user=user)
        return Response({"status": "0", "message": "success"})

    @get_userprofile
    def destroy(self, request, user, pk=None):
        ids = request.data.get("ids[]", [])
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
        try:
            message = request.data["message"]
        except KeyError:
            return FailedResponse.invalid_data(request.data.keys(), ["message"])
        now = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        Models.Care.objects.create(
            user=user,
            message=message,
            created_at=now,
            updated_at=now,
            member_id=user.id,
            reply_id=1,
        )
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
