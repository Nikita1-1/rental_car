from django.urls import path 
from django.contrib.auth import views as auth_views
from user_auths import views as user_auths
from user_dashboard import views


app_name = "dashboard"


urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("booking-detail/<booking_id>/", views.booking_detail, name="booking_detail"),
    path("bookings/", views.bookings, name="bookings"),
    path("profile/", views.profile, name="profile"),
    path("booking/<str:booking_id>/cancel/", views.cancel_booking, name="cancel_booking"),
    path("profile/update-dl/", views.dashboard_profile_update, name="profile"),

# Change Password View
    path('change-password/',auth_views.PasswordChangeView.as_view(template_name='user_dashboard/change-password.html',success_url = '/dashboard/password-changed/'),name='change_password'),
    path("password-changed/", views.password_changed, name="password_changed"),

]