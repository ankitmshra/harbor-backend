from rest_framework import serializers
from .models import CartItem, Cart

class CartItemReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartItem
        fields = ['variation', 'quantity']

class CartReadSerializer(serializers.ModelSerializer):
    items = CartItemReadSerializer(many=True)

    class Meta:
        model = Cart
        fields = ['id', 'items','created_at', 'updated_at']

class CartItemWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartItem
        fields = ['variation', 'quantity']
