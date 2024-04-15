from django.db import models
import logging

logger = logging.getLogger(__name__)


class Point(models.Model):
    view = models.IntegerField(default=1)
    like = models.IntegerField(default=5)
    comment = models.IntegerField(default=10)
    share = models.IntegerField(default=20)

    createAt = models.DateTimeField(auto_now_add=True)
    updateAt = models.DateTimeField(auto_now=True)


class Posts(models.Model):
    postId = models.IntegerField(unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    countView = models.IntegerField(default=0)
    countLike = models.IntegerField(default=0)
    countComment = models.IntegerField(default=0)
    countShare = models.IntegerField(default=0)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title

    def calculate_ranking(self) -> int:
        point = Point.objects.first()
        ranking = self.countLike * point.like + self.countComment * \
            point.comment + self.countShare * point.share + self.countView * point.view
        return ranking

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        logger.info(f"Created post '{self.postId}' successfully.")


class Ranking(models.Model):
    post = models.ForeignKey('Posts', on_delete=models.CASCADE)
    daily_ranking = models.IntegerField(default=0)
    weekly_ranking = models.IntegerField(default=0)
    sum_ranking = models.IntegerField(default=0)

    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Ranking - Post: {self.post}, Daily Ranking: {self.daily_ranking}, Weekly Ranking: {self.weekly_ranking}, Sum Ranking: {self.sum_ranking}"
