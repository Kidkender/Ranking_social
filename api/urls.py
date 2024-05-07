
from django.urls import path
from . import views

urlpatterns = [
    path("posts", views.PostListCreate.as_view(), name='post_view'),
    path("posts/get-posts", views.PostsListApiView.as_view(), name='posts_get_view'),
    path("posts/<str:pk>/", views.PostRetrieveUpdateDestroy.as_view(), name="update"),
    path('posts/suburbs', views.FindPostsBySuburbsIdApiView.as_view(),
         name="get-posts-by-suburbs"),
    path('posts/<str:id>/suburbs', views.PostsNearByListApiView.as_view(),
         name="get-posts-nearby-list"),
    path("ranking", views.RankingView.as_view(), name="ranking_view"),
    path("ranking/<str:pk>", views.RankingRetrieveByIDView.as_view(),
         name="retrieve_by_id_view"),
    path("ranking/post/<str:post_id>/", views.RankingRetrieveByPostView.as_view(),
         name="retrieve_by_post_id_view"),

    path('ranking/postid/<post_id>/',
         views.RankingByPostIDApiView.as_view(), name='ranking-by-post-ID'),

    path("point", views.PointApiView.as_view(), name='point_view'),
    path("point/<int:pk>/", views.PointUpdateApiView.as_view(), name='point_update'),
    path("suburbs", views.SuburbsApiListView.as_view(), name="suburbs_view"),
    path("suburbs/<str:pk>", views.SuburbsRetrieveApiView.as_view(),
         name="suburb-retrieve"),
    path("suburbs/<str:pk>/postcode", views.SuburbsNearByPostcodeApiView.as_view(),
         name="suburb-retrieve-by-postcode"),
    path("users", views.UserListCreateApiView.as_view(), name="users_create_list"),
    path("users/<str:pk>", views.UserRetrieveDestroyApiView.as_view(),
         name="users_retrieve_destroy_view")
]
