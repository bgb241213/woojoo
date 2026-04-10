from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('',      views.SalesListView.as_view(),   name='list'),
    path('<int:pk>/', views.SalesDetailView.as_view(), name='detail'),
]
