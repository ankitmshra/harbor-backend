from django.urls import path
from .views import UpdateDataView, StyleListView, CategoryListView, StyleWithProductsView

app_name = 'alphabroder_integration'

urlpatterns = [
    path('update-data/', UpdateDataView.as_view(), name='update-data'),
    path('getstyles/', StyleListView.as_view(), name='style-list'),
    path('getcategories/', CategoryListView.as_view(), name='get-categories'),
    path('products/<str:style_number>/', StyleWithProductsView.as_view(), name='style-products'),
    # other url patterns...
]