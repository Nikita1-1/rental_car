from django.urls import path

from car import views 

app_name='car_main'

urlpatterns = [
    path("", views.index, name='home'),
    path("select/<slug:slug>/", views.car_detail_page, name="car_detail"),
    path('add-trip/<slug:slug>/', views.add_trip_to_session, name='add_trip_to_session'),

    path("detail/<booking_id>/generate_pdf/", views.generate_booking_pdf, name="generate_booking_pdf"),
    path("selected_car/", views.selected_car, name="selected_car"),
    path('checkout/<str:booking_id>/', views.checkout, name="checkout"),
    path('update_booking_status/<int:booking_id>/', views.update_booking_status, name="update_booking_status"),
    path('admin/booking/<str:booking_id>/update_pdf/', views.update_pdf, name='update_pdf'),
    #Payment routs 
    path('api/create_checkout_session/<str:booking_id>/', views.create_checkout_session, name='api_checkout_session'),
    path("success/<booking_id>", views.payment_success, name="payment_success"),
    path("failed/<booking_id>", views.payment_failed, name="failed"),
]