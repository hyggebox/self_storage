from random import randint

from dateutil.relativedelta import relativedelta

import qrcode

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from phonenumber_field.modelfields import PhoneNumberField
from pytils.translit import slugify

from storage_app.managers import StorageQuerySet, BoxQuerySet, BoxOrderQuerySet


class Storage(models.Model):
    """Склад где расположены боксы."""

    address = models.TextField(
        'адрес',
        help_text='ул. Манчестерская, д. 7, кв. 1'
    )
    longitude = models.FloatField('долгота')
    latitude = models.FloatField('широта')
    phone = PhoneNumberField("телефон склада", blank=True, db_index=True)
    alias = models.CharField(
        'запоминающееся название',
        unique=True,
        max_length=128,
        blank=True
    )
    first_square_meter_price = models.DecimalField(
        'стоимость аренды за первый квадратный метр, руб/кв.м.',
        max_digits=5,
        decimal_places=2,
        blank=True,
        default=599
    )
    rest_square_meters_price = models.DecimalField(
        'стоимость аренды за все последующие квадратные метры кроме первого, руб/кв.м.',
        max_digits=5,
        decimal_places=2,
        blank=True,
        default=150
    )
    temperature = models.FloatField(
        'температура',
        blank=True,
        default=17
    )
    image = models.ImageField(
        'изображение',
        blank=True,
        null=True
    )
    description = models.TextField(
        'описание',
        help_text='Склад у метро.',
        blank=True,
        null=True
    )
    contacts = models.TextField(
        'контакты',
        help_text='Мы находимся на ул. Манчестерская, д. 7, кв. 1. Телефон 7900000000.',
        blank=True,
        null=True
    )
    driving_directions = models.TextField(
        'схема проезда',
        help_text='После ул. Ленина поверните направо...',
        blank=True,
        null=True
    )

    objects = StorageQuerySet.as_manager()

    def count_min_box_price(self):
        min_box_price = self.boxes.aggregate(models.Min('month_rent_price'))['month_rent_price__min']

        return min_box_price

    def count_squares_meters(self):
        squares_meters_count = self.boxes.aggregate(models.Sum('size'))['size__sum']

        return squares_meters_count

    def count_free_squares_meters(self):
        rented_squares_meters_count = self.boxes.filter(is_rented=True).aggregate(models.Sum('size'))['size__sum']
        free_squares_meters_count = self.count_squares_meters() - rented_squares_meters_count

        return free_squares_meters_count

    def count_free_boxes(self):
        free_boxes_count = self.boxes.count() - self.boxes.filter(is_rented=True).count()

        return free_boxes_count

    def slugify_alias(self):
        slugified_alias = slugify(self.alias)

        return slugified_alias

    class Meta:
        verbose_name = 'склад'
        verbose_name_plural = 'склады'

    def __str__(self):
        return f'{self.alias}'


class Box(models.Model):
    """Боксы доступные к аренде."""

    storage = models.ForeignKey(
        Storage,
        on_delete=models.CASCADE,
        verbose_name='склад',
        related_name='boxes'
    )
    size = models.PositiveIntegerField(
        'размер бокса в квадратных метрах',
        validators=[MinValueValidator(1), MaxValueValidator(20),]
    )
    length = models.FloatField(
        'длинна',
        blank=True,
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(20),]
    )
    width = models.FloatField(
        'ширина',
        blank=True,
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(20),]
    )
    height = models.FloatField(
        'высота',
        blank=True,
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(20),]
    )
    floor = models.PositiveIntegerField(
        'этаж',
        blank=True,
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(4),]
    )
    month_rent_price = models.IntegerField(
        'стоимость аренды на месяц',
        blank=True
    )
    is_rented = models.BooleanField('Бокс арендован', blank=True, default=False)

    objects = BoxQuerySet.as_manager()

    def count_month_rent_price(self):
        first_meter_price = self.storage.first_square_meter_price
        rest_meters_price = self.storage.rest_square_meters_price

        total_price = first_meter_price + (self.size - 1) * rest_meters_price

        return total_price

    def calculate_area(self):
        area = self.length * self.width

        return area

    def save(self, *args, **kwargs):
        self.month_rent_price = self.count_month_rent_price()

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'бокс'
        verbose_name_plural = 'боксы'

    def __str__(self):
        return f'Бокс №{self.id}'


class Client(models.Model):
    """Клиент сервиса."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    phone = PhoneNumberField(
        "телефон",
        db_index=True
    )

    class Meta:
        verbose_name = 'клиент'
        verbose_name_plural = 'клиенты'

    def __str__(self):
        return str(self.phone)


class BoxOrder(models.Model):
    """Заказ на аренду бокса."""

    box = models.ForeignKey(
        Box,
        on_delete=models.PROTECT,
        verbose_name = 'бокс',
        related_name='orders'
    )
    rent_term = models.PositiveIntegerField(
        'срок аренды бокса в месяцах',
        validators=[MinValueValidator(1), MaxValueValidator(12)],
    )
    rent_start = models.DateField('начало срока аренды бокса', auto_now_add=True)
    rent_end = models.DateField('конец срока аренды бокса', null=True)
    client = models.ForeignKey(
        Client,
        verbose_name='клиент',
        related_name='orders',
        on_delete=models.PROTECT
    )
    access_code = models.IntegerField(
        'Код для открытия',
        blank=True,
        null=True
    )
    access_qr = models.ImageField(
        'QR-код для открытия',
        blank=True,
        null=True
    )

    objects = BoxOrderQuerySet.as_manager()

    def save(self, *args, **kwargs):
        self.box.is_rented = True
        self.box.save()

        super().save(*args, **kwargs)

        self.rent_end = self.rent_start + relativedelta(months=self.rent_term)

        super().save(*args, **kwargs)

        access_code = randint(10000, 100000)
        self.access_code = access_code
        qr = qrcode.make(access_code)
        qr.save(f'media/qr/{self.box}.png')
        self.access_qr = f'qr/{self.box}.png'

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.box.is_rented = False
        self.box.save(*args, **kwargs)

        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'{self.box} на {self.rent_term} месяцев'
