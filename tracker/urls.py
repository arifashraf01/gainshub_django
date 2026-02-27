from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('setup/', views.setup_profile, name='setup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('log-meal/', views.log_meal, name='log_meal'),
    path('delete-meal/<int:meal_id>/', views.delete_meal, name='delete_meal'),
    path('logout/', views.logout_user, name='logout'),
]
