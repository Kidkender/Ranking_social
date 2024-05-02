
from django.urls import path
from . import views

urlpatterns = [
    path("posts", views.PostListCreate.as_view(), name='post_view'),
    path("posts/<int:pk>/", views.PostRetrieveUpdateDestroy.as_view(), name="update"),
    path('posts/suburbs/<int:id>/', views.FindPostsBySuburbsIdApiView.as_view(),
         name="get-posts-by-suburbs"),
    path('posts/<int:id>/suburbs', views.PostsNearByListApiView.as_view(),
         name="get-posts-nearby-list"),
    path("ranking", views.RankingView.as_view(), name="ranking_view"),
    path("ranking/<int:pk>/", views.RankingRetrieveByIDView.as_view(),
         name="retrieve_by_id_view"),
    path("ranking/post/<int:post_id>/", views.RankingRetrieveByPostView.as_view(),
         name="retrieve_by_post_id_view"),

    path('ranking/postid/<post_id>/',
         views.RankingByPostIDApiView.as_view(), name='ranking-by-post-ID'),

    path("point", views.PointApiView.as_view(), name='point_view'),
    path("point/<int:pk>/", views.PointUpdateApiView.as_view(), name='point_update'),
    path("suburbs", views.SuburbsApiListView.as_view(), name="suburbs_view"),
    path("suburbs/<int:pk>", views.SuburbsRetrieveApiView.as_view(),
         name="suburb-retrieve"),
    path("suburbs/<int:pk>/postcode", views.SuburbsNearByPostcodeApiView.as_view(),
         name="suburb-retrieve-by-postcode")
]
