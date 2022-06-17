import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.mail import send_mail

from storage_app.models import BoxOrder


class Command(BaseCommand):

    help = 'Отправляет email при истечении сроков аренды бокса'

    def handle(self, *args, **kwargs):

        current_date = datetime.date.today()

        for box in BoxOrder.objects.all():
            rent_term = (box.rent_end - current_date).days
            if 0 < rent_term <= 30:
                try:
                    send_mail(
                        subject = 'Срок аренды бокса истекает',
                        message=f'Истекает срок аренды бокса. Осталось {rent_term} дней. '
                                f'Не забудьте забрать свои вещи или продлить аренду!',
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[f'{box.client.user.email}']
                    )
                except:
                    print(f'Сбой отправки для {box.client.user.email}')
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
                    print(f'Сбой отправки для {box.client.user.email}')
                    continue
            elif rent_term >= -180:
                send_mail(
                    subject='Срок аренды бокса истек',
                    message=f'Срок аренды бокса истек {(180 + rent_term)} дней назад. '
                            f'Забрать вещи из бокса невозможно!',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[f'{box.client.user.email}']
                )
                except:
                    print(f'Сбой отправки для {box.client.user.email}')
                    continue