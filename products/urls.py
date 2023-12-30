from django.urls import path
from .views import ProductsListView, CategoryListView, VerboseProductsView

app_name = 'alphabroder_integration'

urlpatterns = [
    path('', ProductsListView.as_view(), name='products-list'),
    path('categories/', CategoryListView.as_view(), name='categories-list'),
    path('<str:product_number>/', VerboseProductsView.as_view(), name='product-variations'),
    # other url patterns...
]