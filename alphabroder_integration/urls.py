from django.urls import path
from .views import UpdateDataView, GetALPProductsView

app_name = 'alphabroder_integration'

urlpatterns = [
    path('update-data/', UpdateDataView.as_view(), name='update-data'),
    path('getproducts/', GetALPProductsView.as_view(), name='getproducts'),
    # other url patterns...
]