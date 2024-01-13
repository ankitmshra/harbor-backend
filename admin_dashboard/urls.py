from django.urls import path

from .views.login import loginview
from .views.dashboard import dashboardview

urlpatterns = [
    path('login/', loginview, name='loginview'),
    path('dashboard/', dashboardview, name='dashboardview'),
]