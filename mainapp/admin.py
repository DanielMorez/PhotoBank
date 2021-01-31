from django.contrib import admin
from django.utils.safestring import mark_safe

from .model_static import RusLang, EstLang, StaticImage, Review,\
                            Media, Portfolio, ServiceAndPrice

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


class StaticImageAdminForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['background'].help_text = mark_safe('<span style="color:red;">Загружайте изображения с разрешением не меньше чем {}x{}'.format(
            *StaticImage.MIN_RESOLUTION_BACK
        ))
        self.fields['about'].help_text = mark_safe('<span style="color:red;">Загружайте изображения с разрешением не меньше чем {}x{}'.format(
            *StaticImage.MIN_RESOLUTION_ABOUT
        ))
        self.fields['review'].help_text =mark_safe('<span style="color:red;">Загружайте изображения с разрешением не меньше чем {}x{}'.format(
            *StaticImage.MIN_RESOLUTION_REVIEW
        ))

    def clean_background(self):
        image = self.cleaned_data['background']
        img = Image.open(image)
        min_width, min_height = StaticImage.MIN_RESOLUTION_BACK
        if img.width < min_width or img.height < min_height:
            raise ValidationError("Загруженное изображение меньше минимального")
        return image

    def clean_about(self):
        image = self.cleaned_data['about']
        img = Image.open(image)
        min_width, min_height = StaticImage.MIN_RESOLUTION_ABOUT
        if img.width < min_width or img.height < min_height:
            raise ValidationError("Загруженное изображение меньше минимального")
        return image

    def clean_review(self):
        image = self.cleaned_data['review']
        img = Image.open(image)
        min_width, min_height = StaticImage.MIN_RESOLUTION_REVIEW
        if img.width < min_width or img.height < min_height:
            raise ValidationError("Загруженное изображение меньше минимального")
        return image

class StaticImageAdmin(admin.ModelAdmin):

    form = StaticImageAdminForm

admin.site.register(Album)
admin.site.register(Photo, PhotoAdmin)
admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Customer)
admin.site.register(PhotoType)
admin.site.register(Watermark, WatermarkAdmin)
admin.site.register(Order)
admin.site.register(RusLang)
admin.site.register(EstLang)
admin.site.register(StaticImage, StaticImageAdmin)
admin.site.register(Review)
admin.site.register(Media)
admin.site.register(Portfolio)
admin.site.register(ServiceAndPrice)