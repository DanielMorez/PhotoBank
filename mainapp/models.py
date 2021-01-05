from PIL import Image

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse

User = get_user_model()
# Create your models here.

#1 Album
#2 Product
#3 CartProduct
#4 Cart
#5 Order
#6 Photo type

#7 Customer

def get_product_url(obj, viewname):
    ct_model = obj.__class__.meta.model_name
    return reverse(viewname, kwargs={'ct_model': ct_model, 'slug': obj.slug})

class LatestCategoriesManager:

    @staticmethod
    def get_categories_for_main_page(self):
        products = Album.objects.all().reverse()[:5]
        return products

class LatestCategories:

    objects = LatestCategoriesManager

class Album(models.Model):

    name = models.CharField(max_length=255, verbose_name='Имя категории')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return get_product_url(self, 'choice_type_photo')

class Product(models.Model):

    MIN_RESOLUTION = (400, 400)
    MAX_RESOLUTION = (2400, 4200)
    MAX_IMG_SIZE = 10485760

    class Meta:
        abstract = True

    album = models.ForeignKey(Album, verbose_name='Альбом', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='Имя фотографии')
    slug = models.SlugField(unique=True)
    image = models.ImageField()
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')

    def __str__(self):
        return self.title

class PhotoType(models.Model):

    type_of_photo = models.CharField(max_length=255, verbose_name='Тип фотографии')

    def __str__(self):
        return f'Тип фотографии: {self.type_of_photo}'

class CartProduct(models.Model):

    user = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE, related_name='related_products')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена')

    def __str__(self):
        return f'Продукт: {self.content_object.title} (для корзины)'

class Photo(Product):

    type_of_photo = models.ForeignKey(PhotoType, verbose_name='Тип фотографии', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.album.name} : {self.title}"

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')

class Cart(models.Model):

    owner = models.ForeignKey('Customer', verbose_name='Владелец', on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=True)

    def __str__(self):
        return str(self.id)


class Customer(models.Model):

    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Номер телефона')
    address = models.CharField(max_length=255, verbose_name='Адрес')

    def __str__(self):
        return f'Покупатель: {self.user.first_name} {self.user.last_name}'



