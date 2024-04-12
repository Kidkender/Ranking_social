from rest_framework import serializers
from .models import Posts, Ranking


class PostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = ["id", "postId", "title", "description",
                  "countLike", "countComment", "countShare", "createdAt", "updatedAt"]


class RankingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ranking
        fields = ["id", "post", "daily_ranking",
                  "weekly_ranking", "sum_ranking"]
