from rest_framework import generics, status
from rest_framework.response import Response
from .models import Posts, Ranking, Point
from .serializers import PostsSerializer, RankingSerializer, PointSerializer


class PostListCreate(generics.ListCreateAPIView):
    queryset = Posts.objects.all()
    serializer_class = PostsSerializer

    def delete(self, request, *args, **kwargs):
        Posts.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PostRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Posts.objects.all()
    serializer_class = PostsSerializer
    lookup_field = "pk"


class RankingView(generics.ListAPIView):
    queryset = Ranking.objects.all()
    serializer_class = RankingSerializer


class RankingRetrieveByIDView(generics.RetrieveAPIView):
    queryset = Ranking.objects.all()
    serializer_class = RankingSerializer
    lookup_field = "pk"


class RankingRetrieveByPostView(generics.RetrieveAPIView):
    queryset = Ranking.objects.all()
    serializer_class = RankingSerializer
    lookup_field = "post_id"


class PointListCreateView(generics.ListCreateAPIView):
    queryset = Point.objects.all()
    serializer_class = PointSerializer


class PointUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Point.objects.all()
    serializer_class = PointSerializer
    lookup_field = "pk"
