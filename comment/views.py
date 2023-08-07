from django.shortcuts import render
from rest_framework import generics, permissions
from comment.serializers import CommentSerializer
from comment.models import Comment
from post.permissions import IsAuthorOrAdminPostOwner


# Create your views here.
class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    lookup_field = 'id'

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return IsAuthorOrAdminPostOwner(),
        return permissions.AllowAny(),
