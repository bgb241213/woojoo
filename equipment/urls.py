from django.urls import path
from . import views

app_name = 'equipment'

urlpatterns = [
    path('', views.EquipmentListView.as_view(), name='list'),
    path('compare/', views.EquipmentCompareView.as_view(), name='compare'),
    path('api/by-category/', views.EquipmentByCategoryAPI.as_view(), name='by_category'),
    path('<int:pk>/', views.EquipmentDetailView.as_view(), name='detail'),
]
