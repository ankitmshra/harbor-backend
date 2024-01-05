from rest_framework import viewsets, status
from rest_framework import serializers
from .models import Cart, CartItem
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from products.models import Variations
from .serializers import CartItemWriteSerializer, CartReadSerializer

class CartListView(ListAPIView):
    serializer_class = CartReadSerializer

    def get_queryset(self):
        user = self.request.user
        return Cart.objects.filter(cart__user=user)

class UpdateCartViewset(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemWriteSerializer

    def _process_cart_items(self, request_data, cart):
        items = request_data.get('items', [])

        cart_items = []
        for item_data in items:
            try:
                item = Variations.objects.get(item_number=item_data['variation'])
                quantity = item_data['quantity']
                available = item.quantity
                if quantity <= available:
                    cart_items.append(CartItem(cart=cart, variation=item, quantity=quantity))
                else:
                    return Response({"error": f"quantity should be less than {available}"}, status=status.HTTP_400_BAD_REQUEST)


            except Variations.DoesNotExist:
                raise serializers.ValidationError("Product not found")

        return cart_items

    def create(self, request):
        data = CartItemWriteSerializer(data=request.data)
        data.is_valid(raise_exception=True)

        cart = request.user.cart

        if cart is None:
            cart = Cart.objects.create(user=request.user)

        cart_items = self._process_cart_items(data.validated_data, cart)
        CartItem.objects.bulk_create(cart_items)

        return Response({"message": "Cart updated successfully"}, status=status.HTTP_201_CREATED)

    def update(self, request):
        data = CartItemWriteSerializer(data=request.data)
        data.is_valid(raise_exception=True)

        cart = request.user.cart

        items = data.validated_data.get('items', [])

        if items:
            for item_data in items:
                try:
                    variation = item_data['variation']
                    quantity = item_data['quantity']

                    cart_item = CartItem.objects.get(cart=cart, variation__item_number=variation)
                    available = cart_item.variation.quantity 

                    if quantity <= available:
                        cart_item.quantity = quantity
                        cart_item.save()
                    else:
                        return Response({"error": f"quantity should be less than {available}"}, status=status.HTTP_400_BAD_REQUEST)

                except CartItem.DoesNotExist:
                    return Response({"error": "Cart item not found on the cart"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "Cart updated successfully"})


    def destroy(self, request):
        data = CartItemWriteSerializer(data=request.data)
        data.is_valid(raise_exception=True)

        cart = request.user.cart

        items = data.validated_data.get('items', [])

        if items:
            for item_data in items:
                try:
                    variation = item_data['variation']

                    # Use filter to delete all matching items
                    CartItem.objects.filter(cart=cart, variation__item_number=variation).delete()

                except CartItem.DoesNotExist:
                    return Response({"error": "Cart item not found on the cart"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "Cart updated successfully"})
