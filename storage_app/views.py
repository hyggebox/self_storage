import os
import random
from functools import reduce
from urllib.parse import unquote
from email.mime.image import MIMEImage

import phonenumbers

from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from rest_framework.decorators import api_view
from rest_framework.response import Response


from django.contrib.auth.models import User

from self_storage import settings
from .forms import RegistrationForm
from .models import Storage, Box, Client, Email, BoxOrder


import folium


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


class SignUp(CreateView):
    form_class = RegistrationForm
    success_url = reverse_lazy('my_rent')
    template_name = 'registration/signup.html'


@api_view(['POST'])
def order_api(request):
    if request.method == 'POST':
        order_data = request.data
        print(order_data['user'])
        order = BoxOrder.objects.update_or_create(
            box=Box.objects.get(id=order_data['box']),
            rent_term=1,
            client=Client.objects.get(user=order_data['user']),
        )
        return Response('OK')


def index(request):
    if request.method == 'POST':
        if 'send_email_button' in request.POST:
            email_for_sender = request.POST['EMAIL1']

            try:
                validate_email(email_for_sender)
                Email.objects.get_or_create(email=email_for_sender)
            except ValidationError as e:
                pass

        elif 'login_button' in request.POST:
            user = authenticate(username=request.POST['EMAIL'],
                                password=request.POST['PASSWORD'])
            if user is not None:
                login(request, user)
                return redirect(my_rent)


            return redirect('/?login=1')

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

            return redirect('/?login=1')

        elif 'reset_button' in request.POST:
            user = User.objects.filter(username=request.POST['EMAIL_FORGET']).first()
            if user:
                # TODO - Восстановление пароля
                print(f'>>>>> отправить новый пароль на {user.username}')
        return redirect('/?login=1')

    random_storage = random.choice(Storage.objects.all())
    storage_box_count = random_storage.boxes.count()
    free_box_count = storage_box_count - random_storage.boxes.filter(is_rented=True).count()
    folium_map = create_map()
    context = {
        'storage': random_storage,
        'box_count': storage_box_count,
        'free_box': free_box_count,
        'map': folium_map._repr_html_(),
    }

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
        'boxes': Box.objects.all(),
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

            return redirect(my_rent)
        else:
            if request.POST['PASSWORD_EDIT'] != 'new password':
                current_user.set_password(request.POST['PASSWORD_EDIT'])
                current_user.save()
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
