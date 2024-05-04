from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, RetrieveUpdateAPIView
from .models import Posts, Ranking, Point, Suburbs
from .serializers import PostsSerializer, RankingSerializer, PointSerializer, SuburbsSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework import pagination
from django_filters.rest_framework import DjangoFilterBackend
from .filters import SuburbsFilter
from rest_framework.exceptions import NotFound
from .common.constants import error
import ast


def get_id_from_combined(combined_list):
    suburbs_ids = Suburbs.objects.filter(
        Combined__in=[item[0] for item in combined_list]).values_list('SA1', flat=True)
    return suburbs_ids


def get_post_by_suburbs_id(suburbs_id: int) -> Posts:
    suburb = Suburbs.objects.filter(SA1=suburbs_id).first()
    if not suburb:
        raise NotFound(detail=error.ERROR_SUBURB_NOT_FOUND)

    nearby_list_raw = suburb.Nearby_List
    nearby_list = ast.literal_eval(nearby_list_raw)
    list_ids = list(get_id_from_combined(nearby_list))
    list_ids.append(suburbs_id)
    return Posts.objects.filter(suburbs_id__in=list_ids)


class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000
    page_query_param = 'p'


class PostListCreate(ListCreateAPIView):
    queryset = Posts.objects.all()
    serializer_class = PostsSerializer
    pagination_class = CustomPagination

    def delete(self, request, *args, **kwargs):
        Posts.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PostRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    queryset = Posts.objects.all()
    serializer_class = PostsSerializer
    lookup_field = "pk"


class FindPostsBySuburbsIdApiView(ListAPIView):
    serializer_class = PostsSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        suburbs_id = self.request.query_params.get('id')
        if not suburbs_id:
            return Posts.objects.all()
        return get_post_by_suburbs_id(suburbs_id)

    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PostsNearByListApiView(ListAPIView):
    serializer_class = PostsSerializer

    def get_queryset(self):
        post_id = self.kwargs.get('id')
        post = Posts.objects.filter(id=post_id).first()

        if not post:
            raise NotFound(detail=error.ERROR_POST_NOT_FOUND)

        suburbs_id = post.suburbs.SA1
        return get_post_by_suburbs_id(suburbs_id)

    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class RankingView(ListAPIView):
    queryset = Ranking.objects.all()
    serializer_class = RankingSerializer


class RankingRetrieveByIDView(RetrieveAPIView):
    queryset = Ranking.objects.all()
    serializer_class = RankingSerializer
    lookup_field = "pk"


class RankingRetrieveByPostView(RetrieveAPIView):
    queryset = Ranking.objects.all()
    serializer_class = RankingSerializer
    lookup_field = "post_id"


class PointApiView(ListAPIView):
    queryset = Point.objects.all()
    serializer_class = PointSerializer


class PointUpdateApiView(RetrieveUpdateAPIView):
    queryset = Point.objects.all()
    serializer_class = PointSerializer
    lookup_field = "pk"


class RankingByPostIDApiView(RetrieveAPIView):
    serializer_class = RankingSerializer

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        post = Posts.objects.filter(postId=post_id).first()

        if not post:
            raise NotFound(detail=error.ERROR_POST_NOT_FOUND)
        return Ranking.objects.filter(post=post)

    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SuburbsApiListView(ListAPIView):
    queryset = Suburbs.objects.all()
    serializer_class = SuburbsSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = SuburbsFilter


class SuburbsRetrieveApiView(RetrieveAPIView):
    queryset = Suburbs.objects.all()
    serializer_class = SuburbsSerializer
    lookup_field = "pk"


class SuburbsNearByPostcodeApiView(RetrieveAPIView):
    serializer_class = SuburbsSerializer

    def get_queryset(self):
        suburbs_id = self.kwargs.get('pk')
        suburb = Suburbs.objects.filter(SA1=suburbs_id).first()
        if suburb:
            return suburb
        else:
            return None

    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset:
            serializer = self.get_serializer(queryset)
            data = serializer.data
            nearby_list_raw = data.get('Nearby_List', [])
            nearby_list = ast.literal_eval(nearby_list_raw)

            list_ids = get_id_from_combined(nearby_list)

            return Response(list_ids)
        else:
            return Response({'error': error.ERROR_SUBURB_NOT_FOUND}, status=404)
