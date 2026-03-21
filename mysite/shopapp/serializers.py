from rest_framework import serializers

from shopapp.models import Product, Order


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = 'pk', 'name', 'price', 'discount', 'description', 'created_at', 'archived', 'preview'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__' # Все поля, включая связанные сущности - products