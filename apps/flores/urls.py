from django.urls import path
from . import views

app_name = 'flores'

urlpatterns = [
    path('', views.home, name='home'),
]
