from django.contrib import admin

from .models import Address, PhoneNumber

admin.site.register(PhoneNumber)
admin.site.register(Address)
