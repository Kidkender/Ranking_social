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


class RankingByPostCodeApiView(generics.RetrieveAPIView):
    serializer_class = RankingSerializer

    def get_queryset(self):
        post_code = self.kwargs.get('post_code')
        post = Posts.objects.filter(postCode=post_code).first()
        if post:
            return Ranking.objects.filter(post=post)
        else:
            return None

    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': 'Post with the given postCode does not exist.'}, status=404)


class RankingByPostIDApiView(generics.RetrieveAPIView):
    serializer_class = RankingSerializer

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        post = Posts.objects.filter(postId=post_id).first()
        if post:
            return Ranking.objects.filter(post=post)
        else:
            return None

    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': 'Post with the post ID is not found.'}, status=404)
