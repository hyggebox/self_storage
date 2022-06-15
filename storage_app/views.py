from django.shortcuts import render
from django.contrib.auth.decorators import login_required


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
