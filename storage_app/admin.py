from django.contrib import admin
from django import forms

from storage_app.models import Storage, Box, BoxOrder, Client, Email


class MyBoxOrderAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            kwargs['initial']
            self.fields['box'].queryset = Box.objects.filter(is_rented=False)
        except KeyError:
            pass


@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    pass


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    readonly_fields = ['size', 'month_rent_price', 'is_rented']


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    pass


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    readonly_fields = ['send_at']


@admin.register(BoxOrder)
class BoxOrderAdmin(admin.ModelAdmin):
    readonly_fields = ['rent_start', 'rent_end']
    form = MyBoxOrderAdminForm
