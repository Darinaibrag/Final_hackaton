from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from config.tasks import send_booking_notification_task
from booking.send_email import send_booking_notification
from post.models import Post

# Create your models here.
User = get_user_model()


class BookingStatus(models.TextChoices):
    in_process = 'in_process'
    completed = 'completed'


class BookingItem(models.Model):
    user = models.ForeignKey(User, related_name='items', on_delete=models.CASCADE)
    booking = models.ForeignKey('Booking', related_name='items', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='booking_items')
    quantity = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f'{self.post.title}'


class Booking(models.Model):
    user = models.ForeignKey(User, related_name='bookings', on_delete=models.CASCADE)
    post = models.ManyToManyField(Post, through=BookingItem)
    number = models.CharField(max_length=150)
    status = models.CharField(max_length=20, choices=BookingStatus.choices, default=BookingStatus.in_process)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.id} ----> {self.user}'


@receiver(post_save, sender=BookingItem)
def booking_post_save(sender, instance, created, *args, **kwargs):
    if created:
        send_booking_notification_task.delay(instance.user.email, instance.booking.id)
