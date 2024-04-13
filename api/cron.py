from django_cron import CronJobManager, CronJobBase, Schedule
from .models import Posts, Ranking
import logging

reset_rank_point = 0
RUN_AT_TIMES = ['00:00']

logger = logging.getLogger(__name__)


class UpdateDailyRankingCronJob(CronJobBase):
    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'update_daily_ranking_cron_job'

    def do(self):
        for ranking in Ranking.objects.all():
            ranking.daily_ranking = reset_rank_point
            ranking.save()
        logger.info('Reset daily ranking successfully')


class UpdateWeeklyRankingCronJob(CronJobBase):
    schedule = Schedule(run_at_times=RUN_AT_TIMES, run_on_days=['mon'])
    code = 'update_weekly_ranking_cron_job'

    def do(self):
        for ranking in Ranking.objects.all():
            ranking.weekly_ranking = reset_rank_point
            ranking.save()
        logger.info('Reset weekly ranking successfully')


cron_manager = CronJobManager(
    [UpdateDailyRankingCronJob, UpdateWeeklyRankingCronJob])
