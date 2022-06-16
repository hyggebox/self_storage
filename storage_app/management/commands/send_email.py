import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.mail import send_mail

from storage_app.models import BoxOrder


class Command(BaseCommand):

    help = 'Отправляет email при истечении сроков аренды бокса'

    def handle(self, *args, **kwargs):
        subject = 'Срок аренды бокса истекает'
        current_date = datetime.date.today()

        for box in BoxOrder.objects.all():
            rent_term = box.rent_end - current_date
            if (days := rent_term.days) <= 30:
                try:
                    send_mail(
                        subject=subject,
                        message=f'Истекает срок аренды бокса. Осталось {days} дней. '
                                f'Не забудьте забрать свои вещи или продлить аренду!',
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[f'{box.client.user.email}']
                    )
                except:
                    print(f'Сбой отправки для {box.client.user.email}')
                    continue
