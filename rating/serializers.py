from rest_framework import serializers
from rating.models import Rating


class RatingSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.email')
    post = serializers.ReadOnlyField(source='post.title')

    class Meta:
        model = Rating
        fields = '__all__'
