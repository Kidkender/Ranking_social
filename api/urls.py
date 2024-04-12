
from django.urls import path
from . import views

urlpatterns = [
    path("posts/", views.PostListCreate.as_view(), name='post_view'),
    path("posts/<int:pk>/", views.PostRetrieveUpdateDestroy.as_view(), name="update"),
    path("ranking", views.RankingView.as_view(), name="ranking_view"),
    path("ranking/<int:pk>/", views.RankingRetrieveByIDView.as_view(),
         name="retrieve_by_id_view"),
    path("ranking/post/<int:post_id>/", views.RankingRetrieveByPostView.as_view(),
         name="retrieve_by_post_id_view"),
]
