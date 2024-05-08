import ast
import logging

from django.db.models import Case, F, IntegerField, Q, Value, When
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import pagination, status
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.generics import (ListAPIView, ListCreateAPIView,
                                     RetrieveAPIView, RetrieveUpdateAPIView,
                                     RetrieveUpdateDestroyAPIView)
from rest_framework.response import Response
from rest_framework.views import APIView

from .common.constants import error
from .common.helpers import preprocessing_data
from .filters import PostsFilter, SuburbsFilter
from .models import Point, Posts, Ranking, Suburbs, Users
from .serializers import (PointSerializer, PostsSerializer,
                          PostSuburbsSerializer, PostUpdateSerializer,
                          RankingSerializer, SuburbsSerializer, UserSerializer)

logger = logging.getLogger(__name__)


def get_id_from_combined(combined_list):
    """
        Retrieve SA1 codes from combined area names.

        Parameters:
            combined_list (list of tuples): A list of combined area names and post IDs.

        Returns:
            list: A list of SA1 codes corresponding to the combined area names.
    """
    combined_lists = [item[0] for item in combined_list]

    suburbs = Suburbs.objects.filter(
        Combined__in=combined_lists)

    suburbs_mapping = {suburb.Combined: suburb.SA1 for suburb in suburbs}

    suburbs_ids = []
    for combined in combined_lists:
        if combined in suburbs_mapping:
            suburbs_ids.append(suburbs_mapping[combined])
        else:
            logger.error(f'Suburbs {combined}  not found in database.')
            continue

    return suburbs_ids


def get_post_by_suburbs_id(suburbs_id: str) -> Posts:
    """
    Returns a list of posts sorted by the order of nearby suburbs and ranking.

    Parameters:
        suburbs_id (str): The ID of the suburbs to fetch posts for.

    Returns:
        QuerySet: A queryset containing the filtered and sorted posts.

    Raises:
        NotFound: If the suburb with the given `suburbs_id` is not found.
    """

    suburb = Suburbs.objects.filter(SA1=suburbs_id).first()
    if not suburb:
        raise NotFound(detail=error.ERROR_SUBURB_NOT_FOUND)

    nearby_list_raw = suburb.Nearby_List
    nearby_list = ast.literal_eval(nearby_list_raw)
    list_ids = list(get_id_from_combined(nearby_list))
    list_ids.insert(0, suburbs_id)

    filter_conditions = [Q(suburbs_id=id) for id in list_ids]

    combined_filter = filter_conditions.pop()
    for condition in filter_conditions:
        combined_filter |= condition

    posts = Posts.objects.filter(combined_filter)

    annotated_posts = posts.annotate(
        sum_ranking=F('ranking__sum_ranking'),
        suburbs_index=Case(
            *[When(suburbs_id=id, then=pos)
              for pos, id in enumerate(list_ids)],
            default=Value(len(list_ids)),
            output_field=IntegerField(),
        )
    )

    sorted_posts = annotated_posts.order_by('suburbs_index', '-sum_ranking')

    return sorted_posts


def get_post_sort_by_ranking():
    annotated_posts = Posts.objects.annotate(
        sum_ranking=F('ranking__sum_ranking'))
    sorted_posts = annotated_posts.order_by('-sum_ranking')

    return sorted_posts


class CustomPagination(pagination.PageNumberPagination):

    page_size = 10
    page_size_query_param = 'size'
    max_page_size = 1000
    page_query_param = 'page'

    def get_page_number(self, request, paginator):
        page_number = request.query_params.get(self.page_query_param) or 0

        if page_number in self.last_page_strings:
            page_number = paginator.num_pages
        new_page = int(page_number) + 1
        return str(new_page)


class PostsListApiView(APIView):
    serializer_class = PostsSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return Posts.objects.all()

    def get_type(self, data):
        return type(data)

    def post(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not request.data:
            queryset_ranking = get_post_sort_by_ranking()
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset_ranking, request)
            serializer = self.serializer_class(
                page, many=True)

            return paginator.get_paginated_response(serializer.data)

        hashTag = request.data.get("hashtag", None)
        suburbs = request.data.get("suburbs", [])
        type = request.data.get("type", None)
        excludePosts = request.data.get("excludePosts", [])
        search = request.data.get("search", None)
        data_queryset = []

        change = False
        if suburbs:
            combineds = []
            for suburb_raw in suburbs:
                combineds.append([suburb_raw])
            suburbs_ids = list(get_id_from_combined(combineds))

            data_queryset = self.filter_by_list_suburbs(queryset, suburbs_ids)

            queryset = queryset.filter(postId__in=data_queryset)

        if hashTag is not None:
            hashtags = hashTag.split()
            for tag in hashtags:
                change = True

                queryset = queryset.filter(hashtag__icontains=tag)
        if type is not None:

            change = True
            queryset = queryset.filter(type=type)
        if excludePosts:

            change = True
            queryset = queryset.exclude(postId__in=excludePosts)

        if search is not None:
            change = True
            queryset = queryset.filter(Q(title__icontains=search) | Q(
                description__icontains=search) | Q(hashtag__icontains=search))

        if not change and not queryset:
            queryset_ranking = get_post_sort_by_ranking()
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset_ranking, request)
            serializer = self.serializer_class(
                page, many=True)
            return paginator.get_paginated_response(serializer.data)

        annotated_posts = queryset.annotate(
            sum_ranking=F('ranking__sum_ranking'))
        sorted_posts = annotated_posts.order_by('-sum_ranking')

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(sorted_posts, request)
        serializer = self.serializer_class(
            page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def filter_by_list_suburbs(self, queryset, suburbs_ids):
        primary_suburbs = []
        nearby_suburbs = []

        for suburb_id in suburbs_ids:
            suburb = Suburbs.objects.filter(SA1=suburb_id).first()

            if not suburb:
                raise NotFound(detail=error.ERROR_SUBURB_NOT_FOUND)

            primary_suburbs.append(suburb_id)

            nearby_list_raw = suburb.Nearby_List
            nearby_list = ast.literal_eval(nearby_list_raw)

            list_nearby_ids = list(get_id_from_combined(nearby_list))

            nearby_suburbs.extend(list_nearby_ids)

        primary_suburbs = list(set(primary_suburbs))
        nearby_suburbs = list(set(nearby_suburbs))
        final_suburbs_order = primary_suburbs + nearby_suburbs
        sorted_posts = []

        for suburb_id in final_suburbs_order:
            posts = queryset.filter(suburbs_id=suburb_id)
            annotated_posts = posts.annotate(
                sum_ranking=F('ranking__sum_ranking'),
                suburbs_index=Value(final_suburbs_order.index(suburb_id)),
            )
            sorted_posts.extend(annotated_posts)

        sorted_posts = sorted(sorted_posts, key=lambda x: (
            x.suburbs_index, -x.sum_ranking))
        return sorted_posts


class PostListCreate(ListCreateAPIView):
    queryset = Posts.objects.all().order_by('createdAt')
    serializer_class = PostsSerializer
    pagination_class = CustomPagination

    def delete(self, request, *args, **kwargs):
        Posts.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        postId = request.data.get("postId")

        if not postId:
            return Response({"message": "postId is required."}, status=status.HTTP_400_BAD_REQUEST)

        existing_post = Posts.objects.filter(postId=postId).first()

        if existing_post:
            logging.error(f"Post {postId} exists in database.")
            return Response({"message": "postId already exists, no action taken."}, status=status.HTTP_200_OK)

        if "suburbs" in request.data:
            data_copy = request.data.copy()
            suburbs_raw = data_copy.get("suburbs")
            if suburbs_raw is not None:
                del data_copy["suburbs"]
                suburb_converted = preprocessing_data.convert_raw_suburbs(
                    suburbs_raw)
                suburb = Suburbs.objects.none()
                if isinstance(suburbs_raw, str):
                    suburb = Suburbs.objects.filter(SA1=suburbs_raw).first()
                else:

                    suburb = Suburbs.objects.filter(
                        Combined=suburb_converted).first()

                data_copy['suburbs'] = suburb.SA1 if suburb else None

            request._request.POST = data_copy

        serializer = self.get_serializer(data=data_copy)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def filter_queryset(self, queryset):

        userId = self.request.data.get("userId", None)
        hashTag = self.request.data.get("hashtag", None)
        suburbs = self.request.data.get("suburbs", [])
        type = self.request.data.get("type", None)
        excludePosts = self.request.data.get("execludePosts", [])

        if userId is not None:
            queryset = queryset.filter(user=userId)
        if hashTag is not None:
            hashtags = hashTag.split()
            for tag in hashtags:
                queryset = queryset.filter(hashtag__icontains=tag)
        if type is not None:
            queryset = queryset.filter(type=type)
        if excludePosts:
            queryset = queryset.exclude(postId__in=excludePosts)
        if suburbs:
            combineds = []
            for suburb_raw in suburbs:
                combined = preprocessing_data.convert_raw_suburbs(suburb_raw)
                combineds.append([combined])

            suburbs_ids = list(get_id_from_combined(combineds))
            queryset = self.filter_by_list_suburbs(queryset, suburbs_ids)

        if not queryset:
            queryset = Posts.objects.annotate(sum_ranking=F(
                'ranking__sum_ranking')).order_by('-ranking__sum_ranking')
        return queryset

    def filter_by_list_suburbs(self, queryset, suburbs_ids):
        primary_suburbs = []
        nearby_suburbs = []

        for suburb_id in suburbs_ids:
            suburb = Suburbs.objects.filter(SA1=suburb_id).first()

            if not suburb:
                raise NotFound(detail=error.ERROR_SUBURB_NOT_FOUND)

            primary_suburbs.append(suburb_id)

            nearby_list_raw = suburb.Nearby_List
            nearby_list = ast.literal_eval(nearby_list_raw)

            list_nearby_ids = list(get_id_from_combined(nearby_list))

            nearby_suburbs.extend(list_nearby_ids)

        primary_suburbs = list(set(primary_suburbs))

        nearby_suburbs = list(set(nearby_suburbs))

        final_suburbs_order = primary_suburbs + nearby_suburbs
        sorted_posts = []

        for suburb_id in final_suburbs_order:
            posts = queryset.filter(suburbs_id=suburb_id)

            annotated_posts = posts.annotate(
                sum_ranking=F('ranking__sum_ranking'),
                suburbs_index=Value(final_suburbs_order.index(suburb_id)),
            )

            sorted_posts.extend(annotated_posts)

        sorted_posts = sorted(sorted_posts, key=lambda x: (
            x.suburbs_index, -x.sum_ranking))

        return sorted_posts


class PostRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    queryset = Posts.objects.all()
    serializer_class = PostUpdateSerializer
    lookup_field = "pk"


class FindPostsBySuburbsIdApiView(ListAPIView):
    serializer_class = PostSuburbsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PostsFilter

    def get_queryset(self):
        suburbs_id = self.request.query_params.get('id')
        if not suburbs_id:
            return Posts.objects.annotate(sum_ranking=F('ranking__sum_ranking')).order_by('-ranking__sum_ranking')

        return get_post_by_suburbs_id(suburbs_id)

    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PostsNearByListApiView(ListAPIView):
    serializer_class = PostsSerializer

    def get_queryset(self):
        post_id = self.kwargs.get('id')
        post = Posts.objects.filter(postId=post_id).first()

        if not post:
            raise NotFound(detail=error.ERROR_POST_NOT_FOUND)

        if not post.suburbs:
            raise ParseError(detail=error.ERROR_SUBURB_NOT_EXIST, code=400)

        suburbs_id = post.suburbs
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


class UserListCreateApiView(ListCreateAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination


class UserRetrieveDestroyApiView(RetrieveUpdateDestroyAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    lookup_field = "pk"
