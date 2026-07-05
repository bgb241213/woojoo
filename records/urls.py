from django.urls import path
from . import views

app_name = 'records'

urlpatterns = [
    path('', views.RecordsListView.as_view(), name='list'),
]
