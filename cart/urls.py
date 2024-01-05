from django.urls import path
from .views import CartListView, UpdateCartViewset

app_name = "cart"

urlpatterns = [
    path("", CartListView.as_view(), name="cart-list"),
    path("items/", UpdateCartViewset.as_view({'post': 'create', 'put': 'update', 'delete': 'destroy'}), name="update-cart"),
]