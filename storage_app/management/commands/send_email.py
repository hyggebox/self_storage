import datetime
import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

from storage_app.models import BoxOrder

logger = logging.getLogger(__name__)

def send_emails():
    current_date = datetime.date.today()

    for box in BoxOrder.objects.all():
        rent_term = (box.rent_end - current_date).days
        if 0 < rent_term <= 30:
            try:
                send_mail(
                    subject='Срок аренды бокса истекает',
                    message=f'Истекает срок аренды бокса. Осталось {rent_term} дней. '
                            f'Не забудьте забрать свои вещи или продлить аренду!',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[f'{box.client.user.email}']
                )
            except:
                logger.info(f'Сбой отправки для {box.client.user.email}')
                continue
        elif -180 <= rent_term <= 0:
            try:
                price = box.box.size * box.box.storage.first_square_meter_price
                target_date = (current_date + datetime.timedelta(180 + rent_term)).strftime('%d.%m.%Y')
                send_mail(
                    subject='Срок аренды бокса истек',
                    message=f'Срок аренды бокса истек {(180 + rent_term)} дней назад. '
                            f'Стоимость месячной аренды - {price} рублей. '
                            f'После {target_date} забрать вещи из бокса будет невозможно!',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[f'{box.client.user.email}']
                )
            except:
                logger.info(f'Сбой отправки для {box.client.user.email}')
                continue
        elif rent_term >= -180:
            try:
                send_mail(
                    subject='Срок аренды бокса истек',
                    message=f'Срок аренды бокса истек {(180 + rent_term)} дней назад. '
                            f'Забрать вещи из бокса невозможно!',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[f'{box.client.user.email}']
                )
            except:
                logger.info(f'Сбой отправки для {box.client.user.email}')
                continue


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):

    help = 'Отправляет email при истечении сроков аренды бокса'

    def handle(self, *args, **kwargs):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), 'default')

        scheduler.add_job(
            send_emails,
            trigger=CronTrigger(day='*/1'),
            id="send_emails",
            max_instances=1,
            replace_existing=True
        )
        logger.info("Added daily job: 'send_emails'")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week='mon', hour='00', minute='00'
            ),
            id='delete_old_job_executions',
            max_instances=1,
            replace_existing=True
        )
        logger.info("Added weekly job: 'delete_old_job_executions'")

        try:
            logger.info('Starting scheduler...')
            scheduler.start()
        except KeyboardInterrupt:
            logger.info('Stopping scheduler...')
            scheduler.shutdown()
            logger.info('Sheduler shut down successfully!')
