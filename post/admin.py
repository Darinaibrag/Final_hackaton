from django.contrib import admin
from .models import Post, PostImages

admin.site.register(PostImages)


class ImageInLineAdmin(admin.TabularInline):
    model = PostImages
    fields = ('image',)
    max_num = 3


@admin.register(Post)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [ImageInLineAdmin, ]
