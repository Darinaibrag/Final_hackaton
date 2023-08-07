from django.db import models
from account.models import CustomUser
from category.models import Category


# Create your models here.
class Post(models.Model):
    STATUS_CHOICES = (
        ('Available', 'available'),
        ('Not available', 'not available')
    )
    title = models.CharField(max_length=255, unique=True)
    body = models.TextField(blank=True)
    owner = models.ForeignKey(CustomUser, related_name='posts', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    preview = models.ImageField(upload_to='images/', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    availability = models.CharField(choices=STATUS_CHOICES, max_length=50, default='Available')
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True)

    def __str__(self):
        return f'{self.owner} -- {self.title[:50]}'

    class Meta:
        ordering = ['created_at']


class PostImages(models.Model):
    title = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='images/')
    post = models.ForeignKey(Post, related_name='images', on_delete=models.CASCADE)

    def generate_name(self):
        from random import randint
        return 'image' + str(self.id) + str(randint(100000, 1_000_000))

    def save(self, *args, **kwargs):
        self.title = self.generate_name()
        return super(PostImages, self).save(*args, **kwargs)
