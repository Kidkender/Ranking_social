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
        fields = ["postId", "title", "description", "type", "hashtag", "ranking", "suburbs", "combined", "countView",
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
        fields = ["SA1", "SAL", "SAL_CODE_2021", "Suburb", "State",
                  "Council", "Postcode", "Combined",
                  "Latitude",
                  "Longitude", "CBD", "Nearby",
                  "Nearby_Dis",
                  "Nearby_Dis_List",
                  "Nearby_List",
                  "Nearby_List_Codes",
                  "Good_Schools", "Beach", "Train"]
