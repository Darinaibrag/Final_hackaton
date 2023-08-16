from django.db.models import Avg
from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.views import APIView
import random
from comment.serializers import CommentSerializer, CommentActionSerializer
from like.models import Favorites, Like
from comment.models import Comment
from rating.serializers import RatingSerializer
from .models import Post, PostImages
from .permissions import IsAuthorOrAdmin, IsAuthor
from .serializers import PostCreateSerializer, PostListSerializers, PostDetailSerializer, PostSerializer, \
    PostImagesSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from like.serializers import LikedUserSerializer, FavoritesPostsSerializer
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Value
from django.db.models.functions import Coalesce
from django.db.models.fields import FloatField

# Create your views here.

class StandartResultPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'page'


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    pagination_class = StandartResultPagination
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ('title',)
    filterset_fields = ('title', 'category', 'category__name')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializers
        elif self.action in ('create', 'update', 'partial_update'):
            return PostCreateSerializer
        return PostDetailSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action in ('update', 'partial_update', 'destroy'):
            return [permissions.IsAuthenticated(), IsAuthorOrAdmin()]
        return [permissions.IsAuthenticatedOrReadOnly(), ]

    @action(['GET', 'POST', 'DELETE'], detail=True)
    def likes(self, request, pk):
        post = self.get_object()
        user = request.user
        if request.method == 'POST':
            if user.likes.filter(post=post).exists():
                return Response('This post has already liked', status=201)
            Like.objects.create(owner=user, post=post)
            return Response('Liked', status=201)
        elif request.method == 'DELETE':
            likes = user.likes.filter(post=post)
            if likes.exists():
                likes.delete()
                return Response('Like deleted', status=204)
            return Response('Post is not found', status=404)
        else:
            likes = post.likes.all()
            serializer = LikedUserSerializer(instance=likes, many=True)
            return Response(serializer.data, status=200)

    @action(['GET', 'POST', 'DELETE'], detail=True)
    def comment(self, request, pk):
        post = self.get_object()
        user = request.user
        if request.method == 'POST':
            serializer = CommentActionSerializer(data=request.data, context={'post': post.id, 'owner': user})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        elif request.method == 'DELETE':
            comment_id = self.request.query_params['id']
            comment = post.comments.filter(post=post, pk=comment_id)
            comment.delete()
            return Response('The comment is delete', status=204)
        else:
            comments = post.comments.all()
            serializer = CommentSerializer(instance=comments, many=True)
            return Response(serializer.data, status=200)

    @action(['GET', 'POST', 'DELETE'], detail=True)
    def favorite(self, request, pk):
        post = self.get_object()
        user = request.user
        if request.method == 'POST':
            if user.favorites.filter(post=post).exists():
                return Response('You have already added this post to favorites', status=400)
            Favorites.objects.create(owner=user, post=post)
            return Response('Added to the favorites', status=201)
        elif request.method == 'DELETE':
            favorite = user.favorites.filter(post=post)
            if favorite.exists():
                favorite.delete()
                return Response('Post was removed from favorites', status=204)
            return Response('Post is not found', status=404)
        else:
            favorites = post.favorites.all()
            serializer = FavoritesPostsSerializer(instance=favorites, many=True)
            return Response(serializer.data, status=200)

    @action(['GET', 'POST', 'DELETE'], detail=True)
    def ratings(self, request, pk):
        post = self.get_object()
        user = request.user

        if request.method == 'GET':
            rating = post.ratings.all()
            serializer = RatingSerializer(instance=rating, many=True)
            return Response(serializer.data, status=200)

        elif request.method == 'POST':
            if post.ratings.filter(owner=user).exists():
                return Response('You have already rated this post', status=400)
            serializer = RatingSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(owner=user, post=post)
            return Response(serializer.data, status=201)
        else:
            if not post.ratings.filter(owner=user).exists():
                return Response('You cannot delete because you have not rated this post.', status=400)
            rating = post.ratings.get(owner=user)
            rating.delete()
            return Response('Deleted', status=204)

    @action(detail=True, methods=['GET', 'POST', 'PUT', 'DELETE'])
    def images(self, request, pk=None):
        post = self.get_object()

        if request.method == 'GET':
            images = post.images.all()
            serializer = PostImagesSerializer(images, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = PostImagesSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(post=post)
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)

        elif request.method == 'PUT':
            image_id = request.data.get('id')
            try:
                image = post.images.get(pk=image_id)
            except PostImages.DoesNotExist:
                return Response({"error": "Image not found."}, status=404)

            serializer = PostImagesSerializer(image, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)

        elif request.method == 'DELETE':
            image_id = request.data.get('id')
            try:
                image = post.images.get(pk=image_id)
            except PostImages.DoesNotExist:
                return Response({"error": "Image not found."}, status=404)

            image.delete()
            return Response(status=204)


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size = 10

class TourBotNextPostView(APIView):
    pagination_class = CustomPageNumberPagination

    def get(self, request):
        category_id = 2  # Здесь задайте ID вашей категории

        queryset = Post.objects.annotate(
            avg_rating=Coalesce(Avg('ratings__rating', output_field=FloatField()), Value(0.0))
        ).filter(
            category=category_id
        ).order_by('-avg_rating')

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        if page:
            serializer = PostSerializer(page[0], many=False)
            return paginator.get_paginated_response(serializer.data)

        return Response('No posts found', status=404)

class HotelBotNextPostView(APIView):
    pagination_class = CustomPageNumberPagination

    def get(self, request):
        category_id = 1  # Здесь задайте ID вашей категории

        queryset = Post.objects.annotate(
            avg_rating=Coalesce(Avg('ratings__rating', output_field=FloatField()), Value(0.0))
        ).filter(
            category=category_id
        ).order_by('-avg_rating')

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        if page:
            serializer = PostSerializer(page[0], many=False)
            return paginator.get_paginated_response(serializer.data)

        return Response('No posts found', status=404)



class TourBotRandomView(APIView):
    def get(self, *args, **kwargs):
        queryset = Post.objects.filter(category=2)
        random_post = random.choice(queryset)
        serializer = PostSerializer(random_post, many=False)
        return Response(serializer.data, status=200)

class HotelBotRandomView(APIView):
    def get(self, *args, **kwargs):
        queryset = Post.objects.filter(category=1)
        random_post = random.choice(queryset)
        serializer = PostSerializer(random_post, many=False)
        return Response(serializer.data, status=200)


class PostImagesViewSet(ModelViewSet):
    queryset = PostImages.objects.all()
    serializer_class = PostImagesSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrAdmin]

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        if self.request.user.is_superuser:
            return PostImages.objects.all()
        return PostImages.objects.filter(post__owner=self.request.user)