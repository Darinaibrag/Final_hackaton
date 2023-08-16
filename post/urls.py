from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TourBotNextPostView, HotelBotRandomView, TourBotRandomView, HotelBotNextPostView, PostImagesViewSet
from . import views

router = DefaultRouter()
router.register('', views.PostViewSet)
router.register(r'post-images', PostImagesViewSet)

urlpatterns = [
    path('tour-random/', TourBotRandomView.as_view()),
    path('hotel-random/', HotelBotRandomView.as_view()),
    path('tour-next/', TourBotNextPostView.as_view()),
    path('hotel-next/', HotelBotNextPostView.as_view()),
    path('', include(router.urls)),
]
