from django.shortcuts import render
from rest_framework import generics, permissions
from comment.serializers import CommentSerializer
from like.models import Favorites, Like
from comment.models import Comment
from rating.serializers import RatingSerializer
from .models import Post
from .permissions import IsAuthorOrAdmin, IsAuthor
from .serializers import PostCreateSerializer, PostListSerializers, PostDetailSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from like.serializers import LikedUserSerializer, FavoritesPostsSerializer
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend


# Create your views here.

class StandartResultPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'page'


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    pagination_class = StandartResultPagination
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ('title',)
    filterset_fields = ('title', 'category')
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
            Comment.objects.create(owner=user, post=post)
            return Response('Commented', status=201)
        elif request.method == 'DELETE':
            comment = Comment.objects.filter(owner=user, post=post)
            if comment.exists():
                comment.delete()
                return Response('Comment deleted', status=204)
            return Response('Post is not found', status=404)
        else:
            comment = post.comments.all()
            serializer = CommentSerializer(instance=comment, many=True)
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
