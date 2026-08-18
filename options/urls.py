from django.urls import path
from . import views

app_name = 'options'

urlpatterns = [
    path('', views.OptionsView.as_view(), name='list'),
]
