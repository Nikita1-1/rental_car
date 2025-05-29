from django.dispatch import receiver
from django.utils import timezone
from django.db import models
import shortuuid
#from weasyprint import HTML
from io import BytesIO
from user_auths.models import User
from django.utils.text import slugify
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from user_auths.models import User, Profile
from django_ckeditor_5.fields import CKEditor5Field
from django.core.validators import MinValueValidator, MaxValueValidator
from taggit.managers import TaggableManager
from django.template.loader import render_to_string
from django.db.models.signals import post_delete

RENTAL_STATUS = (
    ("Available", "Available"),
    ("Not Available", "Not Available"),
    ("In Review", "In Review")
)


DELIVERY = [
    ('Pick Up', 'Pick Up'),
    ("Delivery to you", "Delivery to you"),
]

PREPAID_FUEL_PRICE = 150.00

ICON_TYPE = (
    ('Bootstap Icons', 'Bootstap Icons'),
    ('Fontawesome Icons', 'Fontawesome Icons'),
)

DISCOUNT_TYPE = (
    ("Percentage", "Percentage"),
    ("Flat Rate", "Flat Rate"),
)

BABY_SEAT_TYPE = (  
    ('None', 'None'),
    ('Infant Seat', 'Infant Seat'),
    ('Toddler Seat', 'Toddler Seat'),
    ('Boster Seat', 'Booster Seat')
)

ADDITIONAL_BOOKING_FEATURES = (
    ('None', 'None'),
    ('Ski Rack', 'Ski Rack'),
    ('Snowboard rack', 'Snowboard Rack'),
    ('Bike Rack', 'Bike Rack')
)

PAYMENT_STATUS = (
    ("paid", "paid"),
    ("pending", "pending"),
    ("processing", "processing"),
    ("cancel", "cancel"),
    ("initiated", "initiated"),
    ("refunded", "refunded"),
    ("refunding", "refunding"),
    ("unpaid", "unpaid"),
    ('expired', 'expaired'),
    ("failed", "failed")
)
    
class Features(models.Model):
    name = models.CharField(max_length=50)
    desc = models.TextField(max_length=200, null=True, blank=True)
    image = models.FileField(upload_to='car_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.desc[:30]}..." if self.desc else self.name

class Car(models.Model):
    cid = ShortUUIDField(unique=True, length=8, max_length=10)
    make = models.CharField(max_length=40)
    model = models.CharField(max_length=60)
    year = models.CharField(max_length=4, null=False, blank=False)
    description = CKEditor5Field(null=False, blank=False, config_name='extends')
    image = models.FileField(upload_to='car_images/', blank=True, null=True)  # Specify the upload folder
    location = models.CharField(max_length=350)
    status = models.CharField(max_length=20, choices=RENTAL_STATUS, default="Available")
    date = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager(blank=True)
    features = models.ManyToManyField(Features, blank=True)
    featured = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    slug = models.SlugField(null=True, blank=True)
    def __str__(self):
        return f"{self.make} {self.model}"

    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            uuid_key = shortuuid.uuid()
            uniqueid = uuid_key[:4]
            self.slug = slugify(self.title) + "-" + str(uniqueid.lower())
        
        super(Car, self).save(*args, **kwargs) 

    def thumbnail(self):
        return mark_safe("<img src='%s' width='50' height='50' style='object-fit: cover; border-radius: 6px;'/>" % (self.image.url))

    def car_gallery(self):
        return CarGallery.objects.filter(car=self)
    

    

class Booking(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, blank=True, null=True)
    car = models.ForeignKey(Car, on_delete=models.SET_NULL, blank=True, null=True, related_name='bookings')
    payment_status = models.CharField(max_length=120, choices=PAYMENT_STATUS)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    delivery_address = models.CharField(max_length=1000, null=True, blank=True)
    full_name = models.CharField(max_length=1000, null=True, blank=True)
    acknowledged = models.BooleanField(default=False)
    agreement_pdf = models.FileField(upload_to='agreements/', null=True, blank=True)
    agreement_uploaded = models.BooleanField(default=False)
    signature = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length = 150)
    phone = models.CharField(max_length=15)

    deposit = models.DecimalField(max_digits=8, decimal_places=2, default=1000.00)

    check_in_date = models.DateField()
    check_out_date = models.DateField()

    check_in_time = models.TimeField( null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)

    checked_in = models.BooleanField(default=False)
    checked_out = models.BooleanField(default=False)

    checked_in_tracker = models.BooleanField(default=False)
    checked_out_tracker = models.BooleanField(default=False)

    deposit_added = models.BooleanField(default=False)

    total_days = models.PositiveIntegerField(default=0)
   
    is_active = models.BooleanField(default=False)
    
    coupons = models.ManyToManyField("car.Coupon", blank=True, related_name='bookings')
    before_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    saved = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(default=timezone.now)
    stripe_payment_intent = models.CharField(max_length=150, null=True, blank=True)
   
    bid = ShortUUIDField(unique=True, length=10, max_length=15)
    data = models.DateTimeField(auto_now_add=True)
    booking_id = ShortUUIDField(unique=True, length=10, max_length=15)
    success_id = ShortUUIDField(length=300, max_length=505, alphabet="abcdefghijklmnopqrstuvxyz1234567890")
  

    stripe_payment = models.CharField(max_length=1000, null=True, blank=True)
    def __str__(self):
        return f"{self.booking_id} {self.car} {self.profile.user}"
    
    def is_available(self, check_in_date, check_out_date):
        return not (self.check_in_date <= check_out_date and self.check_out_date >= check_in_date)



class Racks_feature(models.Model):
    name = models.CharField(max_length=20, choices=ADDITIONAL_BOOKING_FEATURES, null=True, blank=True, default=None)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=15.00)  # Set default price
    slug = models.SlugField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - ${self.price}"
    
    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug is None:
            uuid_key = shortuuid.uuid()
            uniqueid = uuid_key[:4]
            self.slug = slugify(self.name) + "-" + str(uniqueid.lower())
        super(Racks_feature, self).save(*args, **kwargs)


class BabySeat(models.Model):
    name = models.CharField(max_length=20, choices=BABY_SEAT_TYPE, null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=15.00)  # Set default price
    slug = models.SlugField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - ${self.price}"
    
    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug is None:
            uuid_key = shortuuid.uuid()
            uniqueid = uuid_key[:4]
            self.slug = slugify(self.name) + "-" + str(uniqueid.lower())
        super(BabySeat, self).save(*args, **kwargs)


class Delivery(models.Model):
    delivery = models.CharField(max_length=150, choices=DELIVERY, blank=False, null=False, default='Pick Up')
    price =  models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    slug = models.SlugField(null=True, blank=True)
    

    def __str__(self):
        return f"{self.delivery} - ${self.price}"

    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug is None:
            uuid_key = shortuuid.uuid()
            uniqueid = uuid_key[:4]
            self.slug = slugify(self.delivery) + "-" + str(uniqueid.lower())
        super(Delivery, self).save(*args, **kwargs)

    @property
    def delivery_price(self):
        if self.delivery == 'Pick Up':
            return 0.00
        elif self.delivery == 'Deliver to you':
            return 150.00
        return 0.00

class Booking_Features(models.Model):
    booking = models.ForeignKey(Booking, related_name='booking_features', on_delete=models.CASCADE)
    prepaid_fuel = models.BooleanField(default=False)
    prepaid_fuel_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    additional_driver = models.BooleanField(default=False)
    flight_number = models.CharField(max_length=40, blank=True, null=True)
    delivery = models.ForeignKey(Delivery, on_delete=models.SET_NULL, null=True, blank=True)
    baby_seat = models.ForeignKey(BabySeat, on_delete=models.SET_NULL, null=True, blank=True)
    racks = models.ForeignKey(Racks_feature, on_delete=models.SET_NULL, null=True, blank=True)
    hfid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")

    def __str__(self):
        return f"Booking: {self.booking.booking_id} | Car: {self.booking.car.make} {self.booking.car.model}"


class Coupon(models.Model):
    code = models.CharField(max_length=1000)
    type = models.CharField(max_length=100, choices=DISCOUNT_TYPE, default="Percentage")
    discount = models.IntegerField(default=1, validators=[MinValueValidator(0), MaxValueValidator(100)])
    redemption = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    make_public = models.BooleanField(default=False)
    valid_from = models.DateField()
    valid_to = models.DateField()
    cid = ShortUUIDField(length=10, max_length=25, alphabet="abcdefghijklmnopqrstuvxyz")

    
    def __str__(self):
        return self.code
    
    class Meta:
        ordering =['-id']


class CouponUsers(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    
    full_name = models.CharField(max_length=1000)
    email = models.CharField(max_length=1000)
    mobile = models.CharField(max_length=1000)

    def __str__(self):
        return str(self.coupon.code)
    
    class Meta:
        ordering =['-id']


class CarGallery(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    image = models.FileField(upload_to="car_images/",  blank=True, null=True)
    hgid =  ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")

    def __str__(self):
        return str(self.car)

    class Meta:
        verbose_name_plural = "Car Gallery"


class CarPicturesForTrip(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    trip_image = models.FileField(upload_to="trip_images/", null=True, blank=True) 
    hgid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")

    def __str__(self):
        return str(self.booking)
    
    class Meta:
        verbose_name_plural = 'Car Trip Photos'


class FeaturedCar(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, null=True, blank=True)
    icon_type = models.CharField(max_length=80, null=True, blank=True, choices= ICON_TYPE)
    icon = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)


    def __str__(self):
        return str(self.name)
    
    class Meta:
        verbose_name_plural = 'Car Features'