from rest_framework import serializers
from .models import Posts, Ranking, Point, Suburbs


class RankingPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ranking
        fields = ["daily_ranking", "weekly_ranking", "sum_ranking"]


class PostsSerializer(serializers.ModelSerializer):
    combined = serializers.ReadOnlyField(source='suburbs.Combined')
    ranking = RankingPostSerializer(read_only=True)

    class Meta:
        model = Posts
        fields = ["id", "postId", "title", "description", "ranking", "suburbs", "combined", "countView",
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


class SuburbsSerializer(serializers.ModelSerializer):
    Nearby_List = serializers.JSONField()

    class Meta:
        model = Suburbs
        fields = ["id", "Suburb", "State",
                  "Postcode", "Combined",
                  "Latitude",
                  "Longitude", "Nearby",
                  "Nearby_Dis",
                  "Nearby_Dis_List",
                  "Nearby_List",
                  "Nearby_List_Codes"]
