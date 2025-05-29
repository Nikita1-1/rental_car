import json
from django.contrib import admin
from user_auths.models import User, Profile
from django.contrib.admin import AdminSite
from django.contrib import admin
from car.models import *
from car.admin import *
from django.utils.html import format_html
from django.urls import reverse
from django.apps import AppConfig
from django.db.models.signals import post_migrate

class SuperuserAdminSite(AdminSite):
    def has_permission(self, request):
        return request.user.is_active and request.user.is_superuser


class UserAdmin(admin.ModelAdmin):
    search_fields = ['full_name', 'username']
    list_display = ['username', 'full_name', 'email']
# Register your models here.

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone', 'image', 'drivers_license', 'verified', 'show_license')
    list_filter = ('verified',)
    search_fields = ('user__username', 'full_name', 'phone')
    list_editable = ('verified', 'drivers_license')

    readonly_fields = ('user',)

    def show_license(self, obj):
        if obj.drivers_license:
            url = obj.get_license_url()
            if obj.drivers_license.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                return mark_safe(f'<a href="{url}" target="_blank"><img src="{url}" width="100"/></a>')
            return mark_safe(f'<a href="{url}" target="_blank">View Document</a>')
        return "No license uploaded"
    show_license.short_description = "Driver's License"

    def has_license(self, obj):
        return bool(obj.verified)
    has_license.boolean = True
    has_license.short_description = 'License verified?'

admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)

superuser_admin_site = SuperuserAdminSite(name='superuseradmin')
superuser_admin_site.register(User, UserAdmin)
superuser_admin_site.register(Profile, ProfileAdmin)
superuser_admin_site.register(Booking, BookingAdmin)
superuser_admin_site.register(Car, CarAdmin)
superuser_admin_site.register(Racks_feature, Racks_Admin)
superuser_admin_site.register(BabySeat, Baby_Seats_Admin)
superuser_admin_site.register(Delivery, Delivery_Admin_) 
superuser_admin_site.register(Features, FeaturesAdmin)
superuser_admin_site.register(Coupon, CouponAdmin)