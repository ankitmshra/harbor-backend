# your_app/serializers.py
from rest_framework import serializers
from .models import AlphaBroderProducts


class AlphaBroderProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlphaBroderProducts
        fields = '__all__'
