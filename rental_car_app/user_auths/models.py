import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser 
from django.db.models.signals import post_save
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.html import mark_safe
from django_ckeditor_5.fields import CKEditor5Field
from django.dispatch import receiver
from django.urls import reverse
from shortuuid.django_fields import ShortUUIDField
from django.core.validators import FileExtensionValidator
from rental_car.settings import secure_storage


def user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (instance.user.id, ext)
    return 'user_{0}/{1}'.format(instance.user.id,  filename)

class User(AbstractUser):
    full_name = models.CharField(max_length=1000, null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=100, null=True, blank=True)

    otp = models.CharField(max_length=100, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

ACC_STATUS = (
    ("Rejected", "Rejected"),
    ("Active", "Active"),
    ("Suspended", "Suspended")
) 

def license_upload_path(instance, filename):
# Save files in a secure directory outside of the public media directory
    return f'DL/user_{instance.user.id}/{filename}'
def user_directory_path(instance, filename):
    return f'User_Image/user_{instance.user.id}/{filename}'

class Profile(models.Model):
    pid = ShortUUIDField(length=7, max_length=10, alphabet="abcdefghijklmopqrstuwxyz1234567890")
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=user_directory_path, storage=secure_storage, default="default.jpg", null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    drivers_license = models.FileField(upload_to=license_upload_path, storage=secure_storage,
                                       null=True, blank=True,
                                       validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'pdf'])])
    phone = models.CharField(max_length=15, null=True, blank=True)

    wallet = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    verified = models.BooleanField(default=False)

    date = models.DateField(auto_now_add=True)

    pf_status=models.CharField(max_length=30, choices = ACC_STATUS, default="Active")
    
    class Meta:
            ordering = ["-date"]

    def __str__(self):
        if self.full_name:
            return f"{self.full_name}"
        else: 
            return f"{self.user.username}"
    def get_image_url(self):
        if self.image:
            return reverse('secure_file', kwargs={'path': self.image.name})
        return ''
    
    def get_license_url(self):
        if self.drivers_license:
            return reverse('secure_file', kwargs={'path': self.drivers_license.name})
        return ''
        
    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = self.user.username
        
        try: 
            old_instance = Profile.objects.get(pk=self.pk)
        except Profile.DoesNotExist:
            old_instance = None
        
        if old_instance:
            if old_instance.drivers_license and old_instance.drivers_license != self.drivers_license:
                old_instance.drivers_license.delete(save=False)
            
            if old_instance.image and old_instance.image != self.image:
                old_instance.image.delete(save=False)
            
        
        super(Profile, self).save(*args,**kwargs)

    @property
    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" />' % (self.image))

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created: 
        Profile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
    
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


post_save.connect(save_user_profile, sender=User)