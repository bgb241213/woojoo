from django.urls import path
from . import views

app_name = 'quotes'

urlpatterns = [
    path('', views.QuoteCreateView.as_view(), name='form'),
    path('complete/', views.QuoteCompleteView.as_view(), name='complete'),
    path('callback/', views.CallbackCreateView.as_view(), name='callback'),
]
