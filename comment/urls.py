from django.urls import path
from .views import CommentCreateView, CommentDetailView

urlpatterns = [
    path('', CommentCreateView.as_view()),
    path('<int:id>/', CommentDetailView.as_view())
]
