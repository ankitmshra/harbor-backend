# your_app/serializers.py
from rest_framework import serializers
from .models import Products, Style, Category, Price, Inventory


class AlphaBroderCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category']


class AlphaBroderStyleSerializer(serializers.ModelSerializer):
    front_image = serializers.SerializerMethodField()

    class Meta:
        model = Style
        fields = ['style_number', 'short_description', 'category', 'full_feature_description', 'front_image']

    def get_front_image(self, obj):
        # Get the first product related to the style
        product = Products.objects.filter(style_number=obj).first()
        if product:
            return product.front_image
        return None


class AlphaBroderProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = '__all__'


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = ['price_per_piece', 'price_per_dozen', 'price_per_case', 'retail_price']


class InventorySerializer(serializers.ModelSerializer):
    total_sum = serializers.SerializerMethodField()

    class Meta:
        model = Inventory
        fields = ['total_sum', 'drop_ship']

    def get_total_sum(self, obj):
        fields_to_sum = ['cc', 'cn', 'fo', 'gd', 'kc', 'ma', 'ph', 'td', 'pz', 'bz', 'fz', 'px', 'fx', 'bx', 'gx']
        return sum(getattr(obj, field) for field in fields_to_sum)



class ProductsSerializer(serializers.ModelSerializer):
    inventory = InventorySerializer(read_only=True)
    price = PriceSerializer(read_only=False)  # Change read_only to False

    class Meta:
        model = Products
        fields = ['is_new', 'item_number', 'style_number', 'color_name', 'color_group_code', 'color_code', 'hex_code',
                  'size_group', 'size_code', 'size', 'case_qty', 'weight', 'front_image', 'back_image', 'side_image',
                  'gtin', 'launch_date', 'pms_color', 'size_sort_order', 'mktg_color_number', 'mktg_color_name',
                  'mktg_color_hex_code', 'created_at', 'updated_at', 'inventory', 'price']


class AlphaBroderStyleWithProductsSerializer(serializers.ModelSerializer):
    products = ProductsSerializer(many=True, read_only=True)

    class Meta:
        model = Style
        fields = ['style_number', 'short_description', 'mill_number', 'mill_name', 'category',
                  'markup_code', 'full_feature_description', 'created_at', 'updated_at', 'products']