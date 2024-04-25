from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, RetrieveUpdateAPIView
from .models import Posts, Ranking, Point, Suburbs
from .serializers import PostsSerializer, RankingSerializer, PointSerializer, SuburbsSerializer
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .filters import SuburbsFilter
from .common.constants import error
import ast


def get_id_from_combined(combined_list):
    suburbs_ids = Suburbs.objects.filter(
        Combined__in=[item[0] for item in combined_list]).values_list('id', flat=True)
    return suburbs_ids


class PostListCreate(ListCreateAPIView):
    queryset = Posts.objects.all()
    serializer_class = PostsSerializer

    def delete(self, request, *args, **kwargs):
        Posts.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PostRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    queryset = Posts.objects.all()
    serializer_class = PostsSerializer
    lookup_field = "pk"


class FindPostsBySuburbsIdApiView(ListAPIView):
    serializer_class = PostsSerializer

    def get_queryset(self):
        suburbs_id = self.kwargs.get('id')
        suburb = Suburbs.objects.filter(id=suburbs_id).first()
        if suburb:
            nearby_list_raw = suburb.Nearby_List
            nearby_list = ast.literal_eval(nearby_list_raw)
            list_ids = list(get_id_from_combined(nearby_list))
            list_ids.append(suburbs_id)
            return Posts.objects.filter(suburbs_id__in=list_ids)
        else:
            return Posts.objects.none()

    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': error.ERROR_POST_NOT_FOUND_WITH_SUBURB}, status=404)


class PostsNearByListApiView(ListAPIView):
    serializer_class = PostsSerializer

    def get_queryset(self):
        post_id = self.kwargs.get('id')
        post = Posts.objects.filter(id=post_id).first()

        if not post:
            return Response({'error': error.ERROR_POST_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)

        suburbs_id = post.suburbs.id
        suburb = Suburbs.objects.filter(id=suburbs_id).first()
        if suburb:
            nearby_list_raw = suburb.Nearby_List
            nearby_list = ast.literal_eval(nearby_list_raw)
            list_ids = list(get_id_from_combined(nearby_list))
            list_ids.append(suburbs_id)
            return Posts.objects.filter(suburbs_id__in=list_ids)
        else:
            return Posts.objects.none()

    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': error.ERROR_POST_NOT_FOUND_WITH_SUBURB}, status=404)


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
            return Response({'error': error.ERROR_POST_NOT_FOUND}, status=404)


class SuburbsApiListView(ListAPIView):
    queryset = Suburbs.objects.all()
    serializer_class = SuburbsSerializer
    pagination_class = PageNumberPagination
    pagination_class.page_size = 10
    filter_backends = [DjangoFilterBackend]
    filterset_class = SuburbsFilter


class SuburbsRetrieveApiView(RetrieveAPIView):
    queryset = Suburbs.objects.all()
    serializer_class = SuburbsSerializer
    lookup_field = "pk"


class SuburbsNearByPostcodeApiView(RetrieveAPIView):
    serializer_class = SuburbsSerializer

    def get_queryset(self):
        suburbs_id = self.kwargs.get('id')
        suburb = Suburbs.objects.filter(id=suburbs_id).first()
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
            print("List IDs: ", list_ids)

            return Response(list_ids)
        else:
            return Response({'error': error.ERROR_SUBURB_NOT_FOUND}, status=404)
