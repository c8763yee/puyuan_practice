from rest_framework import serializers
from django.db.models import Model
ALL_FIELDS = '__all__'


def create_serializer(apply_model: Model, apply_fields: str | list[str] = ALL_FIELDS,
                      apply_ro_fields: list[str] = [], **kwargs):

    assert isinstance(apply_fields, (str, list)
                      ), 'apply_fields must be str or list'

    class Serializer(serializers.ModelSerializer):
        class Meta:
            model = apply_model
            fields = apply_fields
            read_only_fields = apply_ro_fields

    return Serializer
