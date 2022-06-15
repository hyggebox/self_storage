from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required


from django.shortcuts import render

from django.contrib.auth.forms import UserCreationForm

from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import RegistrationForm


# def signup(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get('username')
#             raw_password = form.cleaned_data.get('password1')
#             user = authenticate(username=username, password=raw_password)
#             login(request, user)
#             return redirect('index')
#     else:
#         form = UserCreationForm()
#     return render(request, 'registration/signup.html', {'form': form})


class SignUp(CreateView):
    form_class = RegistrationForm
    success_url = reverse_lazy('my_rent')
    template_name = 'registration/signup.html'


def index(request):
    return render(request, 'index.html')


def boxes(request):
    return render(request, 'boxes.html')


def faq(request):
    return render(request, 'faq.html')


@login_required(login_url='/users/login/')
def my_rent(request):
    if True:
        return render(request, 'my-rent.html')
    return render(request, 'my-rent-empty.html')
