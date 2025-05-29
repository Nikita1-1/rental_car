from django.urls import path
from booking import views

app_name = "booking"

urlpatterns = [
    path('check-availability/', views.check_car_availability, name='check_car_availability'),
    path('add_to_selection/',views.add_to_selection, name='add_to_selection'),
    path('select/<slug:slug>/booking-confirmation/', views.booking_info, name='booking_info'),

    path("delete_selection/", views.delete_selection, name="delete_selection"),
]