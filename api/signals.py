from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Posts, Ranking


@receiver(post_save, sender=Posts)
def update_ranking(sender, instance, created, **kwargs):
    new_ranking = instance.calculate_ranking()
    if created:
        Ranking.objects.update_or_create(post=instance, defaults={
            'daily_ranking': new_ranking,
            'sum_ranking': new_ranking})
    else:
        Ranking.objects.filter(post=instance).update(sum_ranking=new_ranking)
