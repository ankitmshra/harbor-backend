from django.urls import path
from .views import UpdateDataView

app_name = 'alphabroder_integration'

urlpatterns = [
    path('update-data/', UpdateDataView.as_view(), name='update-data'),
]