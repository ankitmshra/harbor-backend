from django.db import models
from django.utils import timezone

from django.db import models
from django.contrib.auth import get_user_model
from products.models import Variations  # Import your existing Products model

User = get_user_model()

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_item')
    variation = models.ForeignKey(Variations, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return self.variation.retail_price * self.quantity
    
    def save(self, *args, **kwargs):
        self.cart.updated_at = timezone.now()
        self.cart.save()
        super().save(*args, **kwargs)