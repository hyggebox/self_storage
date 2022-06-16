import random

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views.generic import CreateView
from django.urls import reverse_lazy

from django.contrib.auth.models import User
from .forms import RegistrationForm
from .models import Storage



class SignUp(CreateView):
    form_class = RegistrationForm
    success_url = reverse_lazy('my_rent')
    template_name = 'registration/signup.html'


def index(request):
    if request.method == 'POST':
        if 'EMAIL' in request.POST:
            user = authenticate(username=request.POST['EMAIL'],
                                password=request.POST['PASSWORD'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect(my_rent)
                else:
                    # TODO - Return a 'disabled account' error message
                    ...
            else:
                print('No user')
                # TODO - Return an 'invalid login' error message.
                ...
            return redirect(index)

        elif 'EMAIL_CREATE' in request.POST and request.POST['PASSWORD_CREATE'] == request.POST['PASSWORD_CONFIRM']:
            new_user = User.objects.filter(username=request.POST['EMAIL_CREATE']).first()
            if not new_user:
                user_name = request.POST['NAME'] or ''
                User.objects.create_user(
                    username=request.POST['EMAIL_CREATE'],
                    password=request.POST['PASSWORD_CREATE'],
                    first_name=user_name
                )

        else:
            user = User.objects.filter(username=request.POST['EMAIL_FORGET']).first()
            if user:
                # TODO - Восстановление пароля
                print(f'>>>>> отправить новый пароль на {user.username}')

    random_storage = random.choice(Storage.objects.all())
    storage_box_count = random_storage.boxes.count()
    free_box_count = storage_box_count - random_storage.boxes.filter(is_rented=True).count()
    context = {
        'storage': random_storage,
        'box_count': storage_box_count,
        'free_box': free_box_count,
    }

    return render(request, 'index.html', context)


def boxes(request):
    context = {
        'storages': Storage.objects.all(),
    }
    return render(request, 'boxes.html', context)


def faq(request):
    return render(request, 'faq.html')


@login_required(login_url='/?login=1')
def my_rent(request):
    return render(request, 'my-rent.html')
