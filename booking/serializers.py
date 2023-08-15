from django.db.models import Sum, F
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
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, instance):
        total_price = instance.items.aggregate(total_price=Sum(F('quantity') * F('post__price')))['total_price']
        return total_price or 0

    class Meta:
        model = Booking
        exclude = ('post',)

    def create(self, validated_data):
        posts_data = validated_data.pop('posts')
        request = self.context.get('request')
        user = request.user
        validated_data['user'] = user

        # Create the Booking object
        booking = Booking.objects.create(**validated_data)

        # Create associated BookingItem objects
        for post_data in posts_data:
            post_data['user'] = user  # Set the user for each BookingItem
            BookingItem.objects.create(booking=booking, **post_data)

        return booking

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['posts'] = BookingItemSerializer(
            instance.items.all(), many=True
        ).data
        return representation
