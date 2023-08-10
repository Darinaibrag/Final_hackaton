from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from booking.models import Booking, BookingStatus
from booking.serializers import BookingSerializer
from post.models import Post


class BookingAPIView(ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        user = request.user
        bookings = user.bookings.all()
        serializer = BookingSerializer(
            instance=bookings, many=True
        )
        return Response(serializer.data, status=200)


class BookingConfirmView(RetrieveAPIView):
    def get(self, request, pk):
        booking = Booking.objects.get(pk=pk)
        booking.status = 'completed'
        booking.save()
        return Response({'message': 'You have confirmed the reservation.'}, status=200)
