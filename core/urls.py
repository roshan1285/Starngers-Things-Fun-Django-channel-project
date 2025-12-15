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
    path('api/send-request/<int:user_id>/', views.send_friend_request, name="send_request"),

    path('api/accept-request/<int:user_id>/', views.accept_friend_request, name="accept_friend_request"),
    path('api/reject-request/<int:user_id>/', views.reject_friend_request, name='reject_friend_request'),

    path('test/', views.test_hawkins_view, name='test_hawkins_view'),
    path('wall/<str:frequency>/', views.wall_room, name='wall_room'),
]
