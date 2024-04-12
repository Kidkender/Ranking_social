from django.db import models
from .common import enumeration
from datetime import datetime, timedelta


class Posts(models.Model):
    postId = models.IntegerField(unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    countLike = models.IntegerField(default=0)
    countComment = models.IntegerField(default=0)
    countShare = models.IntegerField(default=0)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def calculate_ranking(self):
        ranking = self.countLike * enumeration.Score.LIKE.value + self.countComment * \
            enumeration.Score.COMMENT.value + self.countShare * enumeration.Score.SHARE.value
        return ranking


class Ranking(models.Model):
    post = models.ForeignKey('Posts', on_delete=models.CASCADE)
    daily_ranking = models.IntegerField(default=0)
    weekly_ranking = models.IntegerField(default=0)
    sum_ranking = models.IntegerField(default=0)

    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ranking - Post: {self.post}, Daily Ranking: {self.daily_ranking}, Weekly Ranking: {self.weekly_ranking}, Sum Ranking: {self.sum_ranking}"
