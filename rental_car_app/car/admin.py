from django.contrib import admin
from car.models import *
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.urls import reverse
from .views import update_pdf
from django.urls import re_path
# Register your models here.

class Car_Images(admin.TabularInline):
    model = CarGallery

class DeliveryAdmin(admin.TabularInline):
    model = Delivery

class Car_Features(admin.TabularInline):
    model = FeaturedCar
    
class Booking_Ft(admin.TabularInline):
    model=Booking_Features

class Trip_Car_Images(admin.TabularInline):
    model = CarPicturesForTrip
    list_display = ['booking', 'hgid', 'booking_id']
    readonly_fields = ['hgid']
    fields = ['booking', 'trip_image']


class CarAdmin(admin.ModelAdmin):
    inlines = [Car_Images, Car_Features]
    search_fields = ['make', 'model', 'year', 'price']
    list_display = ['make', 'model', 'year', 'image', 'status', 'price']


class BookingAdmin(admin.ModelAdmin):
    inlines = [Booking_Ft, Trip_Car_Images]
    search_fields = ['profile', 'car', 'is_active', 'email']
    list_display = ['profile', 'car', 'is_active', 'check_in_date', "check_out_date", "total_price", 'deposit', 'regenerate_pdf_button']

    def baby_seat(self, obj):
        booking_feature = Booking_Features.objects.filter(booking=obj).first()
        if booking_feature and booking_feature.baby_seat:
             return f"${booking_feature.baby_seat.price}"
        return 'No baby seat'
    baby_seat.short_description = 'baby_seat' 

    def regenerate_pdf_button(self, obj):
        url = reverse('car_main:generate_pdf', args=[obj.booking_id])
        return format_html(f'<a class="button" href="{url}"> Regenerate </a>')
    regenerate_pdf_button.short_description = 'PDF Actions'
    regenerate_pdf_button.allow_tags = True

class CouponAdmin(admin.ModelAdmin):
    search_fields = ['code']
    list_display = ['code', 'type', 'redemption', 'date', 'active', 'make_public', 'valid_from', 'valid_to']

class Delivery_Admin_(admin.ModelAdmin):
    search_fields = ['delivery']
    list_display = ['delivery', 'price']

class FeaturesAdmin(admin.ModelAdmin):
    search_fields = ['name', 'desc']
    list_display = ['name', 'image', 'desc']


class Baby_Seats_Admin(admin.ModelAdmin):
    search_fields = ['name', 'price']
    list_display = ['name', 'price']


class Racks_Admin(admin.ModelAdmin):
    search_fields = ['name', 'price']
    list_display = ['name', 'price']

class MyAdminSite(AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            re_path(r'^booking/(?P<booking_id>[\w-]+)/update_pdf/$', self.admin_view(update_pdf), name='update_pdf_view'),
        ]
        return custom_urls + urls
        
admin.site = MyAdminSite(name='myadmin')
admin.site.register(Racks_feature, Racks_Admin)
admin.site.register(BabySeat, Baby_Seats_Admin)
admin.site.register(Delivery, Delivery_Admin_) 
admin.site.register(Features, FeaturesAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(Car, CarAdmin)