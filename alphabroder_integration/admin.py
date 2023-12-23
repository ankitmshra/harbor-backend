from django.contrib import admin

from .models import Products, Style, Category

class ReadOnlyModelAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Category, ReadOnlyModelAdmin)
admin.site.register(Style, ReadOnlyModelAdmin)
admin.site.register(Products, ReadOnlyModelAdmin)
