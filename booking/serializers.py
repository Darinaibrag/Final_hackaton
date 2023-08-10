from rest_framework import serializers
from booking.models import Booking, BookingItem


class BookingItemSerializer(serializers.ModelSerializer):
    post_title = serializers.ReadOnlyField(source='post.title')

    class Meta:
        model = BookingItem
        fields = ('post', 'post_title', 'quantity')


class BookingSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    user = serializers.ReadOnlyField(source='user.email')
    posts = BookingItemSerializer(write_only=True, many=True)

    class Meta:
        model = Booking
        fields = '__all__'
