from django.urls import path

from . import views

app_name = 'catalog'

urlpatterns = [
    path('',         views.CatalogSalesView.as_view(),   name='sales'),
    path('records/', views.CatalogRecordsView.as_view(), name='records'),
]
