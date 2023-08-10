from django.urls import path
from booking.views import BookingAPIView, BookingConfirmView


urlpatterns = [
    path('', BookingAPIView.as_view()),
    path('confirm/<int:pk>/', BookingConfirmView.as_view())
]
