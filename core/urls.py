from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('landing/', views.landing, name='landing'),
    path('', views.home, name='home'),

    path('sign-up/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    path('api/search/', views.search_users, name='search_users'),
]
