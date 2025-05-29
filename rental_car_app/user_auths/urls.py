from django.urls import path
from user_auths import views

app_name = 'user_auths'

urlpatterns = [
    path('sign-up/', views.RegisterUser, name='sign-up'),
    path('sign-in/', views.LoginUser, name='sign-in'),
    path("logout/", views.LogoutUser, name='logout'),

]