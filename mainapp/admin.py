from django.contrib import admin
from django.utils.safestring import mark_safe
from django.forms import ModelChoiceField, ModelForm, ValidationError

from .models import *

from PIL import Image


class PhotoAdminForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].help_text = mark_safe('<span style="color:red;">Загружайте изображения с минимальным разрешением {}x{}'.format(
            *Product.MIN_RESOLUTION
        ))

    def clean_image(self):
        image = self.cleaned_data['image']
        img = Image.open(image)
        min_width, min_height = Product.MIN_RESOLUTION
        max_width, max_height = Product.MAX_RESOLUTION
        if img.width < min_width or img.height < min_height:
            raise ValidationError("Загруженное изображение меньше минимального")
        if img.width > max_width or img.height > max_height:
            raise ValidationError("Загруженное изображение больше максимального")
        if image.size > Product.MAX_IMG_SIZE:
            raise ValidationError(f"Загруженное изображение больше {self.MAX_IMG_SIZE} Bytes")
        return image

class WatermarkAdminForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].help_text = mark_safe('<span style="color:red;">Загружайте изображения до максимального разрешения {}x{}'.format(
            *Watermark.MAX_RESOLUTION
        ))

    def clean_image(self):
        image = self.cleaned_data['image']
        img = Image.open(image)
        min_width, min_height = Watermark.MIN_RESOLUTION
        max_width, max_height = Watermark.MAX_RESOLUTION
        if img.width < min_width or img.height < min_height:
            raise ValidationError("Загруженное изображение меньше минимального")
        if img.width > max_width or img.height > max_height:
            raise ValidationError("Загруженное изображение больше максимального")
        if image.size > Product.MAX_IMG_SIZE:
            raise ValidationError(f"Загруженное изображение больше {self.MAX_IMG_SIZE} Bytes")
        return image

class PhotoAdmin(admin.ModelAdmin):

    form = PhotoAdminForm


class WatermarkAdmin(admin.ModelAdmin):

    form = WatermarkAdminForm
    # pass
    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == 'album':
    #         return ModelChoiceField(Album.objects.filter(slug='photos'))
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Album)
admin.site.register(Photo, PhotoAdmin)
admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Customer)
admin.site.register(PhotoType)
admin.site.register(Watermark, WatermarkAdmin)
admin.site.register(Order)