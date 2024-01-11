from django.http import Http404

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import AnonRateThrottle, ScopedRateThrottle

from watchlist_app.models import (WatchList, StreamPlatForm, Review)
from watchlist_app.api import (serializers, throttling, permissions)


class UserReview(generics.ListAPIView):
    serializer_class = serializers.ReviewSerializer

    def get_queryset(self):
        username = self.request.query_params.get('username', None)
        return Review.objects.filter(review_user__username=username)
    

class ReviewList(generics.ListAPIView):
    serializer_class = serializers.ReviewSerializer
    throttle_classes = [throttling.ReviewListTrottle, AnonRateThrottle]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['review_user__username', 'active']

    def get_queryset(self):
        pk = self.kwargs['pk']
        return Review.objects.filter(watchlist=pk)
    
    
class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = serializers.ReviewSerializer
    permission_classes = [permissions.IsReviewUserOrReadOnly]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'review-detail'


class ReviewCreate(generics.CreateAPIView):
    serializer_class = serializers.ReviewSerializer
    permission_classes = [IsAuthenticated]
    queryset = Review.objects.all()
    throttle_classes = [throttling.ReviewCreateTrottle]

    def perform_create(self, serializer):
        pk = self.kwargs['pk']
        watchlist = WatchList.objects.get(pk=pk)

        user = self.request.user
        review_queryset = Review.objects.filter(watchlist=watchlist, review_user=user)

        if review_queryset.exists():
            raise ValidationError('You have already reviewed this movie!')
        
        if watchlist.number_rating == 0:
            watchlist.avg_rating = serializer.validated_data['rating']
        else:
            watchlist.avg_rating = (watchlist.avg_rating + serializer.validated_data['rating']) / 2

        watchlist.number_rating += 1
        watchlist.save()
        
        serializer.save(watchlist=watchlist, review_user=user)

        
class StreamPlatFormVS(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminOrReadonly]
    queryset = StreamPlatForm.objects.all()
    serializer_class = serializers.StreamPlatFormSerializer


class WatchListView(APIView):
    permission_classes = [permissions.IsAdminOrReadonly]

    def get(self, request):
        watchlist = WatchList.objects.all()
        serializer = serializers.WatchListSerializer(watchlist, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = serializers.WatchListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
        

class WatchListDetailView(APIView):
    permission_classes = [permissions.IsAdminOrReadonly]

    def get_object(self, pk):
        try:
            return WatchList.objects.get(pk=pk)
        except WatchList.DoesNotExist:
            return Http404
    
    def get(self, request, pk):
        watchlist = self.get_object(pk)
        serializer = serializers.WatchListSerializer(watchlist)
        return Response(serializer.data)
    
    def put(self, request, pk):
        watchlist = self.get_object(pk)
        serializer = serializers.WatchListSerializer(data=request.data, instance=watchlist)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, pk):
        watchlist = self.get_object(pk)
        watchlist.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        