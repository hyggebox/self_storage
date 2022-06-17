import random

import phonenumbers

from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from django.contrib.auth.models import User
from .forms import RegistrationForm
from .models import Storage, Box, Client, Email



class SignUp(CreateView):
    form_class = RegistrationForm
    success_url = reverse_lazy('my_rent')
    template_name = 'registration/signup.html'


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

            print('No user')
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
                    print(formatted_phonenumber, 'is ok')
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
            user = User.objects.filter(username=request.POST['EMAIL_FORGET']).first()
            if user:
                # TODO - Восстановление пароля
                print(f'>>>>> отправить новый пароль на {user.username}')
        return redirect('/?login=1')

    random_storage = random.choice(Storage.objects.all())
    storage_box_count = random_storage.boxes.count()
    free_box_count = storage_box_count - random_storage.boxes.filter(is_rented=True).count()
    context = {
        'storage': random_storage,
        'box_count': storage_box_count,
        'free_box': free_box_count
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
