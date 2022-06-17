# Generated by Django 4.0.5 on 2022-06-17 09:10

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage_app', '0005_box_floor_box_height_box_length_box_width_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='storage',
            name='contacts',
            field=models.TextField(blank=True, help_text='Мы находимся на ул. Манчестерская, д. 7, кв. 1. Телефон 7900000000.', null=True, verbose_name='контакты'),
        ),
        migrations.AddField(
            model_name='storage',
            name='description',
            field=models.TextField(blank=True, help_text='Склад у метро.', null=True, verbose_name='описание'),
        ),
        migrations.AddField(
            model_name='storage',
            name='driving_directions',
            field=models.TextField(blank=True, help_text='После ул. Ленина поверните направо...', null=True, verbose_name='контакты'),
        ),
        migrations.AlterField(
            model_name='box',
            name='floor',
            field=models.PositiveIntegerField(blank=True, default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(4)], verbose_name='этаж'),
        ),
    ]