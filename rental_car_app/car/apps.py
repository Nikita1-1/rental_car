# car/apps.py
import json
from django.apps import AppConfig
from django.db.models.signals import post_migrate

class CarConfig(AppConfig):
    name = 'car'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        # Defer heavy imports until registry is ready
        from django_celery_beat.models import IntervalSchedule, PeriodicTask

        def create_periodic_tasks(sender, **kwargs):
            schedule, _ = IntervalSchedule.objects.get_or_create(
                every=45, period=IntervalSchedule.MINUTES
            )
            PeriodicTask.objects.get_or_create(
                name='Delete expired bookings',
                defaults={
                    'interval': schedule,
                    'task': 'car.tasks.delete_expired_bookings',
                    'args': json.dumps([]),
                }
            )

        post_migrate.connect(create_periodic_tasks, sender=self)
        
        import car.signals
