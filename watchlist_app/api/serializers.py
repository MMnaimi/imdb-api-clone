from rest_framework import serializers
from watchlist_app import models


class ReviewSerializer(serializers.ModelSerializer):
    review_user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = models.Review
        exclude = ['watchlist']

class WatchListSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    class Meta:
        model = models.WatchList
        fields = "__all__"


class StreamPlatFormSerializer(serializers.HyperlinkedModelSerializer):
    
    watchlist = WatchListSerializer(many=True, read_only=True)
    class Meta:
        model = models.StreamPlatForm
        fields = "__all__"
