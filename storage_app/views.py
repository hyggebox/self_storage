import random

from django.shortcuts import render

from .models import Storage

def index(request):
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
    return render(request, 'boxes.html')


def faq(request):
    return render(request, 'faq.html')


def my_rent(request):
    if True:
        return render(request, 'my-rent.html')
    return render(request, 'my-rent-empty.html')
