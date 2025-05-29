"""
URL configuration for rental_car project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from rental_car import views
from user_auths.admin import superuser_admin_site
from user_auths.views import secure_file

urlpatterns = [
    path('admin/', superuser_admin_site.urls),
    path('secure_file/<path:path>/', secure_file, name='secure_file'),
    path('legal/', views.legal_page, name='legal'),
    path('faq/', views.faq_page, name='faq'),
    path('contact/', views.contact_page, name='contact'),

    path('user/', include("user_auths.urls", namespace='user_auths')),
    path('', include("car.urls")),
    path('', views.home, name = 'home'),
    path('', include('booking.urls')),
    path("dashboard/", include("user_dashboard.urls")),


    

    path("ckeditor5/", include("django_ckeditor_5.urls")),

]


urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)