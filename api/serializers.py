from rest_framework import serializers
from .models import Posts


class PostsSerializer(serializers.ModelSerializer):
    ranking = serializers.ReadOnlyField()

    class Meta:
        model = Posts
        fields = ["id", "postId", "title", "description",
                  "countLike", "countComment", "countShare", "ranking"]
