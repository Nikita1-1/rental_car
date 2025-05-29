from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Booking

@shared_task
def delete_expired_bookings():
    expiration_time = timezone.now() - timedelta(minutes=45)
    Booking.objects.filter(payment_status__in=['unpaid', 'processing'], created_at__lt=expiration_time).delete()