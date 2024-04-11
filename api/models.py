from django.db import models
from .common import enumeration


class Posts(models.Model):
    postId = models.IntegerField(unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    countLike = models.IntegerField()
    countComment = models.IntegerField()
    countShare = models.IntegerField()
    ranking = models.IntegerField()

    def save(self, *args, **kwargs):
        if not self.ranking:
            self.ranking = self.calculate_raking()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def calculate_raking(self):
        ranking = self.countLike * enumeration.Score.LIKE.value + self.countComment * \
            enumeration.Score.COMMENT.value + self.countShare * enumeration.Score.SHARE.value
        return ranking
