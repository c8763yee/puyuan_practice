from typing import Type

from rest_framework import serializers

from puyuan.const import ALL_FIELDS

from api import logger


def create_serializer(
    apply_model,
    apply_fields: str | list[str] = ALL_FIELDS,
    apply_ro_fields: list[str] = [],
    foreign_key: dict = {},
    exclude: list[str] = [],
    **kwargs
) -> Type[serializers.ModelSerializer]:
    assert isinstance(apply_fields, (str, list)), "apply_fields must be str or list"
    assert isinstance(apply_ro_fields, list), "apply_ro_fields must be list"
    assert isinstance(foreign_key, dict), "foreign_key must be dict"
    assert isinstance(exclude, list), "excluded field must be list"

    class Serializer(serializers.ModelSerializer):
        for foreign_key_name, foreign_key_serializer in foreign_key.items():
            locals()[foreign_key_name] = foreign_key_serializer

        class Meta:
            model = apply_model
            read_only_fields = apply_ro_fields
            extra_kwargs = kwargs

    if exclude:
        setattr(Serializer.Meta, "exclude", exclude)
    else:
        setattr(Serializer.Meta, "fields", apply_fields)

    return Serializer
