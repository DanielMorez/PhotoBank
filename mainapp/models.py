import sys

from PIL import Image

from django.utils import timezone
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.crypto import get_random_string
from io import BytesIO

User = get_user_model()


# Create your models here.

# 1 Album
# 2 Product
# 3 CartProduct
# 4 Cart
# 5 Order
# 6 Photo type

# 7 Customer

def get_product_url(obj, viewname):
    return reverse(viewname, kwargs={
        'album_slug': obj.album.slug,
        'type_of_photo': obj.type_of_photo.type_of_photo,
        'photo_slug': obj.slug
    })



class LatestCategoriesManager:


    def get_queryset(self):
        return super().get_queryset()

    def get_albums_for_left_side(self):
        products = Album.objects.all().reverse()[:5]
        return products


class LatestCategories:
    objects = LatestCategoriesManager


class Album(models.Model):
    name = models.CharField(max_length=255, verbose_name='Имя категории')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    @staticmethod
    def reversed_objects():
        albums = Album.objects.all()
        albums.reverse()
        return albums

    def get_absolute_url(self):
        return reverse('album_detail', kwargs={'slug': self.slug})


class PhotoType(models.Model):
    type_of_photo = models.CharField(max_length=255, verbose_name='Тип фотографии')

    def __str__(self):
        return f'Тип фотографии: {self.type_of_photo}'


class Product(models.Model):
    MIN_RESOLUTION = (500, 500)
    MAX_RESOLUTION = (2400, 4200)
    MAX_IMG_SIZE = 10485760

    class Meta:
        abstract = True

    album = models.ForeignKey(Album, verbose_name='Альбом', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='Имя фотографии')
    slug = models.SlugField(unique=True, default=0)
    image = models.ImageField()
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')

    def __str__(self):
        return self.title

    def slug_save(self):
        """ A function to generate a 5 character slug and see if it has been used and contains naughty words."""

        if len(type(self).objects.filter(slug=self.slug)) > 0 or self.slug is None:  # if there isn't a slug

            self.slug = get_random_string(9)  # create one
            slug_is_wrong = True
            while slug_is_wrong:  # keep checking until we have a valid slug
                slug_is_wrong = False
                other_objs_with_slug = type(self).objects.filter(slug=self.slug)
                if len(other_objs_with_slug) > 0:
                    # if any other objects have current slug
                    slug_is_wrong = True
                if slug_is_wrong:
                    # create another slug and check it again
                    self.slug = get_random_string(5)
        super().save()


class Photo(Product):
    type_of_photo = models.ForeignKey(PhotoType, verbose_name='Тип фотографии', on_delete=models.CASCADE)
    watermark = models.ForeignKey("Watermark", verbose_name='Водяной знак', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.album.name} : {self.title}"

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')

    def save(self, *args, **kwargs):
        self.slug_save()
        image = self.image
        wm = self.watermark.image

        base_image = Image.open(image)
        watermark = Image.open(wm).convert('RGBA')
        width, height = base_image.size
        w_width, w_height = watermark.size

        transparent = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        transparent.paste(base_image, (0, 0))
        for row in range(height // w_height + 1):
            for col in range(width // w_width + 1):
                transparent.paste(watermark, (col * w_width - 50, row * w_height - 50), mask=watermark)

        filestream = BytesIO()
        transparent.save(filestream, 'PNG')
        filestream.seek(0)
        self.image = InMemoryUploadedFile(
            filestream, 'ImageField', f'{self.title}', f'{self.title.split(".")[-1]}/image', sys.getsizeof(filestream),
            None
        )
        super().save(*args, **kwargs)


class Watermark(models.Model):

    MAX_RESOLUTION = (500, 500)
    MIN_RESOLUTION = (100, 100)
    MAX_IMG_SIZE = 1048570
    title = models.CharField(max_length=255, verbose_name='Имя водного знака')
    image = models.ImageField()

    def __str__(self):
        return f'Водяной знак: {self.title}'


class CartProduct(models.Model):
    user = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE, related_name='related_products')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена')

    def __str__(self):
        if self.content_object:
            return f'Продукт: {self.content_object.title} (для корзины)'
        return f'Продукт уже удален'

    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.content_object.price
        super().save(*args, **kwargs)


class Cart(models.Model):
    owner = models.ForeignKey('Customer', null=True, verbose_name='Владелец', on_delete=models.SET_NULL, blank=True)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(default=0, max_digits=9, decimal_places=2, verbose_name='Общая цена')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=True)

    def __str__(self):
        if self.owner:
            return f'Корзина: {str(self.owner)}'
        return f'У корзины нет владельца: {self.id}'


class Customer(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, verbose_name='Пользователь', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Номер телефона')
    address = models.CharField(max_length=255, verbose_name='Адрес')
    device = models.CharField(max_length=200, null=True, blank=True, verbose_name='Девайс')
    orders = models.ManyToManyField('Order', related_name='related_customer', verbose_name='Заказы покупателя')

    def __str__(self):
        if self.user:
            return f'Покупатель: {self.user.first_name} {self.user.last_name}'
        return f'Незарегестрированный пользователь: {self.device}'

class Order(models.Model):

    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'

    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'

    STATUS_CHOICES = (
        (STATUS_NEW, 'Новый заказ'),
        (STATUS_IN_PROGRESS, 'Заказ в обработке'),
        (STATUS_READY, 'Заказ готов'),
        (STATUS_COMPLETED, 'Заказ выполнен')
    )

    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, 'Самовызов'),
        (BUYING_TYPE_DELIVERY, 'Доставка')
    )

    customer = models.ForeignKey(Customer, verbose_name='Покупатель', related_name='related_order', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    cart = models.ForeignKey(Cart, verbose_name='Корзина', on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=1024, verbose_name='Адрес', null=True, blank=True)
    status = models.CharField(max_length=100, verbose_name='Статус заказа', choices=STATUS_CHOICES, default=STATUS_NEW)
    buying_type = models.CharField(max_length=100, verbose_name='Тип заказа', choices=BUYING_TYPE_CHOICES, default=BUYING_TYPE_SELF)
    comment = models.TextField(verbose_name='Комментарий к закаказу', null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания заказа')
    order_date = models.DateTimeField(verbose_name='Дата получения заказа', default=timezone.now)

    def __str__(self):
        return str(self.id)



