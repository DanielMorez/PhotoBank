import sys, os

from PIL import Image
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile
from django.utils.crypto import get_random_string
from io import BytesIO

User = get_user_model()


def get_product_url(obj, viewname):
    return reverse(viewname, kwargs={
        'album_slug': obj.album.slug,
        'type_of_photo': obj.type_of_photo.type_of_photo,
        'photo_slug': obj.slug
    })

def get_upload_to(instance, filename):
    return f'{instance.album.upload_to}/{filename}'

class Album(models.Model):
    name = models.CharField(max_length=255, verbose_name='Имя категории')
    image = models.ImageField(verbose_name='Обложка', null=True, blank=True)
    slug = models.SlugField(unique=True)
    upload_to = models.CharField(max_length=124, verbose_name='Папка загрузки')
    ship_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена доставки', default=0)

    def delete(self, *args, **kwargs):
        # You have to prepare what you need before delete the model
        storage, path = self.image.storage, self.image.path
        # Delete the model before the file
        super(Album, self).delete(*args, **kwargs)
        # Delete the file after the model
        storage.delete(path)

    def __str__(self):
        return self.name

    @staticmethod
    def reversed_objects():
        albums = Album.objects.all()
        albums.reverse()
        return albums

    def get_absolute_url(self):
        return reverse('album_detail', kwargs={'album_slug': self.slug})


class PhotoType(models.Model):
    type_of_photo = models.CharField(max_length=255, verbose_name='Тип фотографии')
    slug = models.CharField(max_length=255, verbose_name='slug_name', null=True, blank=True)

    def __str__(self):
        return f'Тип фотографии #{self.id}: {self.type_of_photo}'


class Product(models.Model):
    MIN_RESOLUTION = (500, 500)
    MAX_RESOLUTION = (5400, 5200)
    MAX_IMG_SIZE = 10485760

    class Meta:
        abstract = True

    album = models.ForeignKey(Album, verbose_name='Альбом', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='Имя фотографии', default='Фото')
    image = models.ImageField(upload_to=get_upload_to, verbose_name='Фотография с водянным знаком', blank=True)

    def __str__(self):
        return self.title


class Photo(Product):

    type_of_photo = models.ForeignKey(PhotoType, verbose_name='Тип фотографии', on_delete=models.CASCADE)
    watermark = models.ForeignKey("Watermark", verbose_name='Водяной знак', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.album.name} : {self.title}"

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')

    def save(self, *args, **kwargs):
        # You have to prepare what you need before delete the model
        storage, path = self.image.storage, self.image.path
        if self.watermark:
            image = self.image
            wm = self.watermark.image
            base_image = Image.open(image)  # Открываем полотно для изображения
            watermark = Image.open(wm).convert('RGBA')  # Устанавливаем цветовую корекцию

            width, height = base_image.size     # Получим размеры водяного знака (вз) и изображения,
            w_width, w_height = watermark.size  # чтобы определить кол-во наложение вз

            transparent = Image.new('RGBA', (width, height), (0, 0, 0, 0))  # Определяем размеры полотна
            transparent.paste(base_image, (0, 0))  # Накладываем изображение на полотно

            # Накладываем вз на полотно
            for row in range(height // w_height + 1):
                for col in range(width // w_width + 1):
                    transparent.paste(watermark, (col * w_width - 50, row * w_height - 50), mask=watermark)

            # Открываем поток на запись изображения
            filestream = BytesIO()
            transparent.save(filestream, 'PNG')
            filestream.seek(0)

            self.image = InMemoryUploadedFile(
                filestream, 'ImageField', f'{image.name}', f'{transparent.format}/image',
                sys.getsizeof(filestream), None
            )
        super().save(*args, **kwargs)

        if self.image.path == path:  # Если есть изменения после сохранения удаляем старую версию
            try: storage.delete(path)  # Удаляем старую версию фото
            except: pass

class Watermark(models.Model):

    MAX_RESOLUTION = (4000, 4000)
    MIN_RESOLUTION = (100, 100)
    title = models.CharField(max_length=255, verbose_name='Имя водного знака')
    image = models.ImageField(upload_to='watermarks')

    def __str__(self):
        return f'Водяной знак: {self.title}'

    def delete(self, *args, **kwargs):
        # You have to prepare what you need before delete the model
        storage, path = self.image.storage, self.image.path
        # Delete the model before the file
        super(Watermark, self).delete(*args, **kwargs)
        # Delete the file after the model
        storage.delete(path)


class Service(models.Model):
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена', default=0)
    service = models.ForeignKey('ServiceAndPrice', verbose_name='Корзина', on_delete=models.CASCADE, related_name='related_service')

    def save(self, *args, **kwargs):
        try:
            self.final_price = self.qty * self.service.price
        except:
            pass
        super().save(*args, **kwargs)

class CartProduct(models.Model):
    user = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE, related_name='related_products')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена', default=0)
    services = models.ManyToManyField('Service', verbose_name='Формат фото', null=True, blank=True)

    def __str__(self):
        if self.content_object:
            return f'Продукт: {self.content_object.title} (для корзины)'
        self.delete()
        return f'Продукт уже удален'

    def save(self, *args, **kwargs):
        try:
            self.final_price = self.services.aggregate(models.Sum('final_price')).get('final_price__sum', 0)
        except:
            pass
        super().save(*args, **kwargs)


class Cart(models.Model):
    owner = models.ForeignKey('Customer', null=True, verbose_name='Владелец', on_delete=models.CASCADE, blank=True)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(default=0, max_digits=9, decimal_places=2, verbose_name='Общая цена')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=True)
    total = models.DecimalField(default=0, max_digits=9, decimal_places=2, verbose_name='Цена с доставкой')

    def __str__(self):
        if self.owner:
            return f'Корзина: {str(self.owner)}'
        return f'У корзины нет владельца: {self.id}'

    def save(self, *args, **kwargs):
        try:
            self.total = self.products.first().content_object.album.ship_price + self.final_price
        except:
            pass
        super().save(*args, **kwargs)



class Customer(models.Model):

    LANG_RUS = 'rus'
    LANG_EST = 'est'

    LANG_TYPES = (
        (LANG_RUS, 'Русский'),
        (LANG_EST, 'Eestlane')
    )

    user = models.ForeignKey(User, null=True, blank=True, verbose_name='Пользователь', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Номер телефона')
    address = models.CharField(max_length=255, verbose_name='Адрес')
    device = models.CharField(max_length=200, null=True, blank=True, verbose_name='Девайс')
    orders = models.ManyToManyField('Order', related_name='related_customer', verbose_name='Заказы покупателя')
    lang = models.CharField(max_length=100, verbose_name='Тип заказа', choices=LANG_TYPES, default=LANG_RUS)
    created_date = models.DateTimeField(auto_now=True, verbose_name='Дата создания')

    def __str__(self):
        if self.user:
            return f'Покупатель: {self.user.first_name} {self.user.last_name}'
        a = len(Session.objects.filter(session_key=self.device))
        if not len(Session.objects.filter(session_key=self.device)):
            self.delete()

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
    email = models.CharField(max_length=1024, verbose_name='Email', null=True, blank=True)
    status = models.CharField(max_length=100, verbose_name='Статус заказа', choices=STATUS_CHOICES, default=STATUS_NEW)
    buying_type = models.CharField(max_length=100, verbose_name='Тип заказа', choices=BUYING_TYPE_CHOICES, default=BUYING_TYPE_SELF)
    comment = models.TextField(verbose_name='Комментарий к закаказу', null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания заказа')
    order_date = models.DateTimeField(verbose_name='Дата получения заказа', default=timezone.now)

    def __str__(self):
        return str(self.id)




