from django.db import models
from account.models import CustomUser
from post.models import Post


# Create your models here.

class Like(models.Model):
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    owner = models.ForeignKey(CustomUser, related_name='likes', on_delete=models.CASCADE)


class Favorites(models.Model):
    owner = models.ForeignKey(CustomUser, related_name='favorites', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='favorites', on_delete=models.CASCADE)
