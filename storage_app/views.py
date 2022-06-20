import os
import random
import string
from functools import reduce
from time import sleep
from urllib.parse import unquote
from email.mime.image import MIMEImage

import folium
import phonenumbers
from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.template import loader
from django.views.generic import CreateView
from django.utils.crypto import get_random_string
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response


from django.contrib.auth.models import User

from self_storage import settings
from .forms import RegistrationForm
from .models import Storage, Box, Client, Email, BoxOrder



def generate_password():
    psw_length = 5
    allowed_chars = string.ascii_lowercase + string.digits
    password = get_random_string(psw_length, allowed_chars=allowed_chars)
    return password


def prepare_storage_object_info_html(storage_object):
    box_rent_button = '<p><b>Есть доступные к аренде боксы.</b></p>' if storage_object.count_free_boxes() > 0 else '<p><b>Все боксы заняты, выберите другой склад.</b></p>'
    storage_object_info_html = """
        <h3>{storage_name}:</h3>
        <p>{address}</p>
        <p>{phone_number}</p>
        <p>Аренда боксов от <b>{min_box_price} руб.</b> в мес.</p>
        <p>{free_squares_meters_count} из {squares_meters_count} м² склада свободно</p>
        <p>{free_boxes_count} из {boxes_count} боксов свободно</p>
        {box_rent_button}
        """.format(
            storage_name=storage_object.alias,
            address=storage_object.address,
            phone_number=storage_object.phone,
            min_box_price=storage_object.count_min_box_price(),
            squares_meters_count=storage_object.count_squares_meters(),
            free_squares_meters_count=storage_object.count_free_squares_meters(),
            boxes_count=storage_object.boxes.count(),
            free_boxes_count=storage_object.count_free_boxes(),
            box_rent_button=box_rent_button
        )

    return storage_object_info_html


def add_storage(folium_map, lat, lon, name, storage_object_info_html, image_url):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(80, 80),
    )

    popup_html = storage_object_info_html.encode('ascii', errors='xmlcharrefreplace').decode('utf-8')

    folium.Marker(
        [lat, lon],
        tooltip=name.encode('ascii', errors='xmlcharrefreplace').decode('utf-8'),
        icon=icon,
        popup=popup_html
    ).add_to(folium_map)



def create_map():
    city_centre = [51.672, 39.1843] # Voronezh centre

    folium_map = folium.Map(location=city_centre, zoom_start=12)

    storages = Storage.objects.all()
    for storage in storages:
        add_storage(
            folium_map,
            storage.latitude,
            storage.longitude,
            storage.alias,
            prepare_storage_object_info_html(storage),
            'https://www.gruzchiki-kiev.net/wp-content/uploads/2021/02/skklad.png'
        )

    return folium_map


@api_view(['POST'])
def order_api(request):
    if request.method == 'POST':
        order_data = request.data
        # BoxOrder.objects.create(
        #     box=Box.objects.get(id=order_data['box']),
        #     rent_term=1,
        #     client=Client.objects.get(user=order_data['user']),
        # )
        box = Box.objects.get(id=order_data['box'])
        client = Client.objects.get(user=order_data['user'])
        order = BoxOrder()
        order.box = box
        order.rent_term = 1
        order.client = client
        order.box.is_rented = True
        order.save()
        return Response('OK')


@api_view(['PUT'])
def extend_rent_api(request):
    if request.method == 'PUT':
        order_data = request.data
        ordered_box = BoxOrder.objects.get(id=order_data['order'])
        # ordered_box.rent_end += relativedelta(month=1)
        ordered_box.rent_term += 1
        ordered_box.save()
        return Response('OK')


def index(request):
    random_storage = random.choice(Storage.objects.all())
    storage_box_count = random_storage.boxes.count()
    free_box_count = storage_box_count - random_storage.boxes.filter(
        is_rented=True).count()
    folium_map = create_map()
    context = {
        'storage': random_storage,
        'box_count': storage_box_count,
        'free_box': free_box_count,
        'map': folium_map._repr_html_(),
        'errors': None
    }

    if request.method == 'POST':
        if 'send_email_button' in request.POST:
            email_for_sender = request.POST['EMAIL1']

            try:
                validate_email(email_for_sender)
                Email.objects.get_or_create(email=email_for_sender)
            except ValidationError as e:
                pass

        elif 'login_button' in request.POST:
            authentificated_user = authenticate(username=request.POST['EMAIL'],
                                                password=request.POST['PASSWORD'])
            if authentificated_user:
                login(request, authentificated_user)
                return redirect(my_rent)

            user_in_db = User.objects.filter(username=request.POST['EMAIL']).first()
            if user_in_db:
                context['errors'] = f'Введён неправильный пароль'
            else:
                context['errors'] = f'Пользователя с почтой {request.POST["EMAIL"]} нет в базе'
            return render(request, 'index.html', context)

        elif 'signup_button' in request.POST and request.POST['PASSWORD_CREATE'] == request.POST['PASSWORD_CONFIRM']:
            new_user = User.objects.filter(username=request.POST['EMAIL_CREATE']).first()
            if not new_user:
                parsed_phonenumber = phonenumbers.parse(request.POST['PHONE'], 'RU')
                if phonenumbers.is_valid_number(parsed_phonenumber):
                    formatted_phonenumber = phonenumbers.format_number(
                        parsed_phonenumber,
                        phonenumbers.PhoneNumberFormat.E164
                    )
                    with transaction.atomic():
                        created_user = User.objects.create_user(
                            username=request.POST['EMAIL_CREATE'],
                            password=request.POST['PASSWORD_CREATE'],
                            first_name=request.POST['NAME']
                        )
                        Client.objects.create(
                            user=created_user,
                            phone=formatted_phonenumber,
                        )
                        login(request, created_user)
                return redirect(my_rent)
            return redirect('/?login=1')

        elif 'reset_button' in request.POST:
            entered_email = request.POST['EMAIL_FORGET']
            user = User.objects.filter(username=entered_email).first()
            with transaction.atomic():
                if user:
                    new_password = generate_password()
                    email_body = f'''
                        <html>
                            <body>
                                <p>Новый пароль: <strong>{new_password}</strong></p>
                                <p>Вы можете изменить его в <a href="{request.get_host()}/?login=1" target="_blank">личном кабинете</a></b></p>
                            </body>
                        </html>
                        '''
                    user.set_password(new_password)
                    user.save()
                else:
                    email_body = f'''
                        <html>
                            <body>
                                <p>Вы не зарегистрированы в сервисе SelfStorage</p>
                                <p>Чтобы зайти в личный кабинет, 
                                <b><a href="{request.get_host()}/?login=1" target="_blank">зарегистрируйтесь</a></b>
                                </p>
                            </body>
                        </html>
                        '''
                email = EmailMessage(
                    subject='Восстановление пароля в сервисе SelfStorage',
                    body=email_body,
                    from_email=settings.EMAIL_HOST_USER,
                    to=[entered_email]
                )
                email.content_subtype = "html"
                email.send()

        return redirect('/?login=1')

    return render(request, 'index.html', context)


def boxes(request):
    if request.method == 'POST':
        if 'send_email_button' in request.POST:
            email_for_sender = request.POST['EMAIL1']

            try:
                validate_email(email_for_sender)
                Email.objects.get_or_create(email=email_for_sender)
            except ValidationError as e:
                pass

    context = {
        'storages': Storage.objects.all(),
        'boxes': Box.objects.filter(is_rented=False).all(),
    }

    return render(request, 'boxes.html', context)


def faq(request):
    return render(request, 'faq.html')


@login_required(login_url='/?login=1')
def my_rent(request):
    if request.method == 'POST':
        current_user = request.user
        if 'open_box' in request.POST:
            order = BoxOrder.objects.get(pk=request.POST['open_box'])
            subject = f'Код для открытия бокса №{order.box.id}'
            body_html = f'''
            <html>
                <body>
                    <p>Код ключа: {order.access_code}</p>
                    <img src="qr-code" />
                </body>
            </html>
            '''
            from_email = settings.EMAIL_HOST_USER
            to_email = current_user.username

            msg = EmailMultiAlternatives(
                subject,
                body_html,
                from_email=from_email,
                to=[to_email]
            )
            msg.mixed_subtype = 'related'
            msg.attach_alternative(body_html, "text/html")
            image = unquote(order.access_qr.name)
            file_path = reduce(os.path.join, ['media', image])
            with open(file_path, 'br') as f:
                img = MIMEImage(f.read())
            msg.attach(img)
            msg.send()
            sleep(4)
            return redirect(my_rent)

        if 'PASSWORD_EDIT' in request.POST:
            if request.POST['PASSWORD_EDIT'] != 'new password':
                current_user.set_password(request.POST['PASSWORD_EDIT'])
                current_user.save()
        if 'PHONE_EDIT'in request.POST:
            if current_user.client.phone != request.POST['PHONE_EDIT']:
                parsed_phonenumber = phonenumbers.parse(request.POST['PHONE_EDIT'], 'RU')
                if phonenumbers.is_valid_number(parsed_phonenumber):
                    formatted_phonenumber = phonenumbers.format_number(
                        parsed_phonenumber,
                        phonenumbers.PhoneNumberFormat.E164
                    )

                current_user.client.phone = formatted_phonenumber
                current_user.client.save()

    return render(request, 'my-rent.html')
