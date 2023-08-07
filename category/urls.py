from django.urls import path
from .views import CategoryCreateListView, CategoryDetailView


urlpatterns = [
    path('', CategoryCreateListView.as_view()),
    path('<int:id>/', CategoryDetailView.as_view())
]
