from typing import Type

from rest_framework import serializers

from puyuan.const import ALL_FIELDS

from api import logger


def create_serializer(apply_model, apply_fields: str | list[str] = ALL_FIELDS,
                      apply_ro_fields: list[str] = [], foreign_key: dict = {},
                      **kwargs) -> Type[serializers.ModelSerializer]:

    assert isinstance(apply_fields, (str, list)
                      ), 'apply_fields must be str or list'

    class Serializer(serializers.ModelSerializer):
        pass

    class Meta:
        model = apply_model
        fields = apply_fields
        read_only_fields = apply_ro_fields
        extra_kwargs = kwargs

    for foreign_key_name, foreign_key_serializer in foreign_key.items():
        setattr(Serializer, foreign_key_name, foreign_key_serializer)

    if 'exclude' in kwargs:
        delattr(Meta, 'fields')
    setattr(Serializer, 'Meta', Meta)
    return Serializer
