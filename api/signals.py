from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Posts, Ranking


@receiver(post_save, sender=Posts)
def update_ranking(sender, instance, created, **kwargs):
    new_sum_ranking = instance.calculate_ranking()
    if created:
        Ranking.objects.update_or_create(post=instance, defaults={
            'sum_ranking': new_sum_ranking})
    else:
        ranking = Ranking.objects.get(post=instance)
        yesterday_sum_ranking = ranking.yesterday_sum_ranking

        new_daily_ranking = new_sum_ranking - yesterday_sum_ranking

        ranking.daily_ranking = new_daily_ranking
        ranking.sum_ranking = new_sum_ranking
        ranking.save()
