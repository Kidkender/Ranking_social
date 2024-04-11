from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Posts


@receiver(post_save, sender=Posts)
def update_ranking(sender, instance, created, **kwargs):
    if created:
        instance.ranking = instance.calculate_raking()
        instance.save()
    else:
        instance.ranking = instance.calculate_raking()
        Posts.objects.filter(id=instance.id).update(ranking=instance.ranking)
