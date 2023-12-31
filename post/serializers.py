from rest_framework import serializers
from comment.serializers import CommentSerializer
from .models import Post, PostImages
from category.models import Category
from like.serializers import LikeSerializer
from django.db.models import Avg, Count


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImages
        fields = '__all__'


class PostListSerializers(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    owner_username = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Post
        fields = ('id', 'title', 'owner', 'category', 'preview', 'owner_username', 'category_name', 'price', 'availability')


class PostCreateSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(required=True, queryset=Category.objects.all())
    images = PostImageSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = ('title', 'body', 'category', 'preview', 'images', 'price')

    def create(self, validated_data):
        request = self.context.get('request')
        post = Post.objects.create(**validated_data)
        images_data = request.FILES.getlist('images')
        for image in images_data:
            PostImages.objects.create(image=image, post=post)
        return post

    def update(self, instance, validated_data):
        request = self.context.get('request')
        images_data = request.FILES.getlist('images')

        instance.title = validated_data.get('title', instance.title)
        instance.body = validated_data.get('body', instance.body)
        instance.category = validated_data.get('category', instance.category)
        instance.preview = validated_data.get('preview', instance.preview)
        instance.price = validated_data.get('price', instance.price)
        instance.save()

        instance.images.all().delete()
        for image in images_data:
            PostImages.objects.create(image=image, post=instance)

        return instance


class PostDetailSerializer(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source='owner.username')
    category_name = serializers.ReadOnlyField(source='category.name')
    images = PostImageSerializer(many=True)

    class Meta:
        model = Post
        fields = '__all__'

    @staticmethod
    def is_liked(post, user):
        return user.likes.filter(post=post).exists()

    @staticmethod
    def is_favorite(post, user):
        return user.favorites.filter(post=post).exists()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['likes'] = LikeSerializer(instance.likes.all(), many=True).data
        representation['quantity of likes'] = 0
        for _ in representation['likes']:
            representation['quantity of likes'] += 1
        representation['comments_count'] = instance.comments.count()
        representation['comments'] = CommentSerializer(instance.comments.all(), many=True).data
        user = self.context['request'].user
        if user.is_authenticated:
            representation['is_liked'] = self.is_liked(instance, user)
            representation['is_favorite'] = self.is_favorite(instance, user)
        representation['rating'] = instance.ratings.aggregate(
            Avg('rating')
        )
        rating = representation
        rating['rating_count'] = instance.ratings.count()
        return representation


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ('title', 'preview', 'price', 'category')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        rating_data = instance.ratings.aggregate(
            avg_rating=Avg('rating'),
            rating_count=Count('rating')
        )
        representation['rating'] = {
            'avg_rating': rating_data['avg_rating'],
            'rating_count': rating_data['rating_count']
        }
        return representation

class PostImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImages
        fields = ('id', 'title', 'image', 'post')
        read_only_fields = ('id', 'title', 'post')

    def create(self, validated_data):
        return PostImages.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance