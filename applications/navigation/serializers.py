from rest_framework import serializers
from django.db import transaction

from applications.navigation.models import Navigations, ModelType


class NavigationsSerializer(serializers.ModelSerializer):
    # 导航内容
    class Meta:
        model = Navigations
        fields = ('id', 'name_navigations', 'url', 'desc', 'image')


class TypeSerializer(serializers.ModelSerializer):
    # 导航分类
    navigations_of = NavigationsSerializer(many=True, read_only=True)
    class Meta:
        model = ModelType
        fields = ('id', 'name_type', 'navigations_of')