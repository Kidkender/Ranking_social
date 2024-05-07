from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, RetrieveUpdateAPIView
from .models import Posts, Ranking, Point, Suburbs, Users
from .serializers import PostsSerializer, RankingSerializer, PointSerializer, SuburbsSerializer, UserSerializer, PostSuburbsSerializer
from django.db.models import Q, F, Value, IntegerField, Case, When

from rest_framework import pagination
from django_filters.rest_framework import DjangoFilterBackend
from .filters import SuburbsFilter, PostsFilter
from rest_framework.exceptions import NotFound
from .common.constants import error
import ast
from django.db.models import Case, When, Value, IntegerField
import logging

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

    # Create a list of Q objects for filtering
    filter_conditions = [Q(suburbs_id=id) for id in list_ids]

    # Combine the filter conditions with OR operator
    combined_filter = filter_conditions.pop()
    for condition in filter_conditions:
        combined_filter |= condition

    # Apply the filter to get all posts in the list of suburbs_ids
    posts = Posts.objects.filter(combined_filter)

    # Annotate each post with sum_ranking and suburbs index
    annotated_posts = posts.annotate(
        sum_ranking=F('ranking__sum_ranking'),
        suburbs_index=Case(
            *[When(suburbs_id=id, then=pos)
              for pos, id in enumerate(list_ids)],
            default=Value(len(list_ids)),
            output_field=IntegerField(),
        )
    )

    # Sort the annotated posts by sum_ranking and suburbs index
    sorted_posts = annotated_posts.order_by('suburbs_index', '-sum_ranking')

    return sorted_posts


def convert_raw_suburbs(raw_suburbs) -> str:
    suburb = raw_suburbs.get("suburb", "")
    state = raw_suburbs.get("state", "")
    post_code = raw_suburbs.get("postCode", "")

    if suburb and state and post_code:
        combined = f"{suburb}, {state} {post_code}"
        return combined
    else:
        return None


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

    def filter_queryset(self, queryset):
        userId = self.request.data.get("userId", None)
        hashTag = self.request.data.get("hashtag", None)
        suburbs = self.request.data.get("suburbs", [])
        type = self.request.data.get("type", None)
        excludePosts = self.request.data.get("execludePosts", [])

        if userId is not None:
            queryset = queryset.filter(user=userId)
        if hashTag is not None:
            queryset = queryset.filter(hashtag=hashTag)
        if type is not None:
            queryset = queryset.filter(type=type)
        if excludePosts:
            queryset = queryset.exclude(postId__in=excludePosts)
        if suburbs:
            combineds = []
            for suburb_raw in suburbs:
                combined = convert_raw_suburbs(suburb_raw)
                combineds.append([combined])

            suburbs_ids = list(get_id_from_combined(combineds))
            queryset = self.filter_by_list_suburbs(queryset, suburbs_ids)
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
    serializer_class = PostsSerializer
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


class UserListCreateApiView(ListCreateAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination


class UserRetrieveDestroyApiView(RetrieveUpdateDestroyAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    lookup_field = "pk"
