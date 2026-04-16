from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('webhook/', views.receive_alert, name='receive_alert'),
]