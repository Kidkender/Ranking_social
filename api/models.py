from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from .common.constants.error import VALIDATOR_VALUE_NON_NEGATIVE, VALIDATOR_SPECTIAL_CHARACTER, VALIDATOR_ONLY_NUMBER
import re
import logging


logger = logging.getLogger(__name__)


def validate_with_spectial_charactor(_value):
    if not re.match(r'^[a-zA-Z0-9]+$', _value):
        raise ValidationError(VALIDATOR_SPECTIAL_CHARACTER)


def only_number(_value):
    if _value.isdigit() == False:
        raise ValidationError(VALIDATOR_ONLY_NUMBER)


def get_default_suburb():
    default_suburb_id = 1
    return default_suburb_id


class Point(models.Model):
    view = models.IntegerField(default=1)
    like = models.IntegerField(default=5)
    comment = models.IntegerField(default=10)
    share = models.IntegerField(default=20)

    createAt = models.DateTimeField(auto_now_add=True)
    updateAt = models.DateTimeField(auto_now=True)


class Suburbs(models.Model):
    SA1 = models.CharField(primary_key=True, unique=True,
                           max_length=100, null=False)
    SAL = models.IntegerField(validators=[
        MinValueValidator(0, VALIDATOR_VALUE_NON_NEGATIVE)])
    SAL_CODE_2021 = models.CharField(max_length=100, blank=False)
    Council = models.TextField()

    Suburb = models.CharField(max_length=100)
    State = models.CharField(max_length=10)
    Postcode = models.IntegerField(default=0, validators=[
        MinValueValidator(0, VALIDATOR_VALUE_NON_NEGATIVE)])
    Combined = models.TextField(max_length=150)

    Latitude = models.FloatField()
    Longitude = models.FloatField()
    CBD = models.FloatField()

    Nearby = models.TextField(null=True)
    Nearby_Dis = models.TextField(null=True)
    Nearby_Dis_List = models.TextField(null=True)
    Nearby_List = models.TextField(null=True)
    Nearby_List_Codes = models.TextField(null=True)

    Good_Schools = models.FloatField(default=0, validators=[
        MinValueValidator(0, VALIDATOR_VALUE_NON_NEGATIVE)])
    Beach = models.BooleanField(default=False)
    Train = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.Combined}'


class Posts(models.Model):
    TYPE_POST_CHOICE = {
        "blog": "blog",
        "video": "video",
        "listing": "listing"
    }

    postId = models.CharField(primary_key=True, unique=True, null=False, blank=False, max_length=255, validators=[
                              validate_with_spectial_charactor])
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(choices=TYPE_POST_CHOICE, default=TYPE_POST_CHOICE.get('blog'),
                            null=False, blank=False, max_length=50)
    hashtag = models.CharField(max_length=100, null=True, blank=True)
    countView = models.IntegerField(
        default=0, validators=[MinValueValidator(0, VALIDATOR_VALUE_NON_NEGATIVE)])
    countLike = models.IntegerField(
        default=0, validators=[MinValueValidator(0, VALIDATOR_VALUE_NON_NEGATIVE)])
    countComment = models.IntegerField(
        default=0, validators=[MinValueValidator(0, VALIDATOR_VALUE_NON_NEGATIVE)])
    countShare = models.IntegerField(
        default=0, validators=[MinValueValidator(0, VALIDATOR_VALUE_NON_NEGATIVE)])
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    suburbs = models.ForeignKey(
        'Suburbs', on_delete=models.CASCADE)
    user = models.ForeignKey('Users', on_delete=models.CASCADE)

    @property
    def ranking(self):
        try:
            return self.ranking_set.first()
        except Ranking.DoesNotExist:
            return None

    def __str__(self) -> str:
        return self.postId

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
    yesterday_sum_ranking = models.IntegerField(default=0)
    sum_ranking = models.IntegerField(default=0)

    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Ranking - Post: {self.post}, Daily Ranking: {self.daily_ranking}, Weekly Ranking: {self.weekly_ranking}, Sum Ranking: {self.sum_ranking}"


class Users(models.Model):
    userId = models.CharField(
        primary_key=True, max_length=100, null=False, blank=False, unique=True, validators=[validate_with_spectial_charactor])
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.userId

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        logging.info(f'Create user {self.userId} successfully.')
