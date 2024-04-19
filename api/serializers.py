from rest_framework import serializers
from .models import Posts, Ranking, Point


class PostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = ["id", "postId", "title", "description", "postCode", "location", "countView",
                  "countLike", "countComment", "countShare", "createdAt", "updatedAt"]


class RankingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ranking
        fields = ["id", "post", "daily_ranking",
                  "weekly_ranking", "sum_ranking"]


class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = ["id", "view", "like", "comment", "share"]
