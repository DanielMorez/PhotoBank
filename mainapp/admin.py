from django.contrib import admin
from django.forms import ModelChoiceField
from django import forms
from .models import *


class PhotoAdmin(admin.ModelAdmin):

    # pass
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='photos'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Category)
admin.site.register(Photo, PhotoAdmin)
admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Customer)
