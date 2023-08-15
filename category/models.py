from django.db import models


# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return f'{self.name} '

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
