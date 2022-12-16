from django.urls import path
from . import views

# app_name = AppName

urlpatterns = [
    path('login/',views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),

    path('', views.home, name='home'),
    path('room_page/<str:pk>/', views.room, name='room'),
    path('create-room/', views.createRoom, name='createRoom'),
    path('update-room/<str:pk>/', views.updateRoom, name='updateRoom'),
    path('delete-room/<str:pk>/', views.deleteRoom, name='deleteRoom'),
    path('login/',views.loginPage, name='login'),

]