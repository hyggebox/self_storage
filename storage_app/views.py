from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


def boxes(request):
    return render(request, 'boxes.html')


def faq(request):
    return render(request, 'faq.html')


def my_rent(request):
    if True:
        return render(request, 'my-rent.html')
    return render(request, 'my-rent-empty.html')
