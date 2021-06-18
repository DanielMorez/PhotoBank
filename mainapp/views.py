import os

from decimal import Decimal

from google.converter import order2list
from google.spreadsheet import parse, insert
from photoBank.settings import MEDIA_ROOT, MEDIA_URL
from django.views.static import serve

from django.contrib.contenttypes.models import ContentType
from django.views.generic import FormView, View

from django.http import JsonResponse

from django.db import transaction

from django.shortcuts import render
from .models import Cart, CartProduct
from django.http import HttpResponseRedirect

from .mixin import CartMixin, LanguageMixin

from .utils import recalc_cart, send_mail, contact_mail

from .models import Photo, Album, PhotoType, Watermark, Service
from .forms import PackageUploadFiles, OrderForm, CartForm

from .model_static import ContactInfo, StaticImage, Review, \
    Media, Portfolio, ServiceAndPrice, PrivacyPoliceModel

from django.utils.crypto import get_random_string


class MainPageView(LanguageMixin, View):

    def get(self, request, *args, **kwargs):
        context = {}
        context['lang'] = self.customer.lang
        context['lang_dict'] = self.lang_model
        context['desktop'] = 'Windows' in request.headers['User-Agent']

        if ContactInfo.objects.count():
            context['contact'] = ContactInfo.objects.last()

        if StaticImage.objects.count():
            context['images'] = StaticImage.objects.last()

        context['reviews'] = Review.objects.all()
        context['portfolio'] = Portfolio.objects.all()
        if Media.objects.count():
            context['media'] = Media.objects.last()

        context['categories'] = set(item.type_of_photo for item in context['portfolio'])
        context['services'] = ServiceAndPrice.objects.all()

        return render(request, 'base.html', context)

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            name = request.POST.get('name')
            email = request.POST.get('email')
            message = request.POST.get('message')
            if name and email and message:
                response = contact_mail(name, email, message)
                return JsonResponse(response, status=200)
        else:
            return JsonResponse({'error': 'Запрос совершен не с помощью AJAX'}, status=200)

class ChangeLang(MainPageView):

    template_name = 'base.html'

    @transaction.atomic
    def get(self, request, *args, **kwargs):
        if self.customer.lang == 'rus':
            self.customer.lang = 'est'
        else:
            self.customer.lang = 'rus'
        self.customer.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class AlbumShowView(LanguageMixin, CartMixin, View):

    template_name = 'album_detail.html'

    def get(self, request, *args, **kwargs):

        context = {
            'images': self.images,
            'lang': self.customer.lang,
            'lang_dict': self.lang_model,
            'cart_counter': self.cart.products.count(),
            'album': Album.objects.get(slug=kwargs['album_slug']),
            'absolute_url': request.build_absolute_uri(),
            'cart': self.cart
        }

        context.update({'photo': list(Photo.objects.filter(album=context['album']))})
        photo_types = set(photo.type_of_photo for photo in context['photo'])
        photo_types = [[t, Photo.objects.filter(type_of_photo=t, album=context['album']).first()] for t in photo_types]
        context.update({'photo_types': photo_types})
        return render(request, self.template_name, context)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            album = Album.objects.get(slug=kwargs['album_slug'])
            old_slug = str(album.slug)
            album.slug = get_random_string(12)
            album.save()
            old_path = MEDIA_ROOT + '\\' + old_slug
            new_path = MEDIA_ROOT + '\\' + str(album.slug)
            try:
                os.rename(old_path, new_path)
            except:
                os.makedirs(new_path)
        return HttpResponseRedirect(album.get_absolute_url())


class TypeAlbumShowView(LanguageMixin, CartMixin, View):

    def get(self, request, *args, **kwargs):
        context = {
            'images': self.images,
            'lang': self.customer.lang,
            'lang_dict': self.lang_model,
            'cart_counter': self.cart.products.count(),
            'album': self.album,
            'photos': Photo.objects.filter(album=self.album, type_of_photo=self.type_of_photo),
            'products_id': self.products_id,
            'photo_type': self.type_of_photo,
            'cart': self.cart
        }
        return render(request, 'album.html', context)


class PhotoShowView(View):

    def get_context_data(self, **kwargs):
        print(kwargs)
        context = super().get_context_data(**kwargs)
        context['album'] = Album.objects.get(slug=kwargs['album_slug'])
        context['photo'] = Photo.objects.get(album=context['album'], slug=kwargs['photo_slug'])
        return context


class UploadFilesView(FormView):
    form_class = PackageUploadFiles
    template_name = 'upload_files.html'
    success_url = '/upload_files/'

    def get(self, request, *args, **kwargs):
        context = {'form': self.form_class}
        try:
            context.update({'images': StaticImage.objects.last()})
        except: pass
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('files')

        if form.is_valid() and 'image' in request.FILES['files'].content_type:
            album = Album.objects.get(pk=request.POST['albums'])
            try:
                watermark = Watermark.objects.get(pk=request.POST['watermarks'])
            except ValueError:
                watermark = None
            photo_type = PhotoType.objects.get(pk=request.POST['photo_type'])
            for file in files:
                one_image = Photo(
                    album=album, title=file.name,
                    image=file, type_of_photo=photo_type,
                    watermark=watermark
                )
                one_image.save()

            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class AddToCartView(CartMixin, View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            content_type = ContentType.objects.get_for_model(Photo)
            content_object = Photo.objects.get(pk=int(request.POST['photo_id']))
            services = ServiceAndPrice.objects.filter(type_of_photo=content_object.type_of_photo)
            cart_product, created = CartProduct.objects.get_or_create(
                user=self.customer, cart=self.cart, content_type=content_type,
                object_id=content_object.id,
            )
            for s in services:
                service = Service.objects.create(qty=1, final_price=s.price, service=s)
                cart_product.services.add(service)
            cart_product.save()
            self.cart.products.add(cart_product)
            recalc_cart(self.cart)
            return JsonResponse({'cart_counter': self.cart.products.count(), 'action': '/remove/', }, status=200)


class CartView(LanguageMixin, CartMixin, View):

    def get(self, request):
        context = {
            'cart': self.cart,
            'images': self.images,
            'lang': self.customer.lang,
            'lang_dict': self.lang_model,
            'cart': self.cart,
            'album': self.album,
            'cart_counter': self.cart.products.count(),
        }
        return render(request, 'cart.html', context)

class CheckoutView(LanguageMixin, CartMixin, View):

    def get(self, request, *args, **kwargs):
        context = {
            'images': self.images,
            'cart': self.cart,
            'album': self.album,
            'lang': self.customer.lang,
        }
        return render(request, 'checkout.html', context)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            last_name = request.POST.get('last_name')
            first_name = request.POST.get('first_name')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            comment = request.POST.get('comment')
            if self.cart.products.count() == 0:
                return JsonResponse(
                    {'cart_counter': 0, 'message': 'Ваша корзина пуста. Скорее всего вы уже отправили заявку!'
                                                   ' Перенаправляем вас на главную :)'}, status=404)
            if last_name and first_name and phone and email:
                form = OrderForm(request.POST or None)
                if form.is_valid():
                    new_order = form.save(commit=False)
                    new_order.customer = self.customer
                    new_order.first_name = form.cleaned_data['first_name']
                    new_order.last_name = form.cleaned_data['last_name']
                    new_order.phone = form.cleaned_data['phone']
                    new_order.address = form.cleaned_data['email']
                    new_order.comment = form.cleaned_data['comment']
                    self.cart.in_order = True
                    new_order.cart = self.cart
                    new_order.save()
                    self.cart.save()
                    response = send_mail(email, first_name, last_name, phone, comment, self.cart)
                    return JsonResponse({'cart_counter': 0, 'email': response}, status=200)

class DeleteFromCartView(CartMixin, View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            content_type = ContentType.objects.get_for_model(Photo)
            content_object = Photo.objects.get(pk=int(request.POST['photo_id']))
            cart_product, created = CartProduct.objects.get_or_create(
                user=self.customer, cart=self.cart, content_type=content_type, object_id=content_object.id
            )
            self.cart.products.remove(cart_product)
            recalc_cart(self.cart)
            cart_product.delete()
            context = {
                'cart_counter': self.cart.products.count(),
                'action': '/add/',
                'final_price': self.cart.final_price,
                'total_price': self.cart.total,
                'message': 'Товар успешно удален!',
                'album': self.album,
            }
            return JsonResponse(context, status=200)


class MakeOrderView(CartMixin, View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            last_name = request.POST.get('last_name')
            first_name = request.POST.get('first_name')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            comment = request.POST.get('comment')
            if not self.cart.products.count() and None not in self.cart.products.all():
                return JsonResponse({'cart_counter': 0, 'message': 'Ваша корзина пуста. Скорее всего вы уже отправили заявку!'
                                                                   ' Перенаправляем вас на главную :)',
                                     'album': '/'}, status=404)

            if last_name and first_name and phone and email:
                form = OrderForm(request.POST or None)
                if form.is_valid():
                    album_slug = self.cart.products.last().content_object.album.slug
                    new_order = form.save(commit=False)
                    new_order.customer = self.customer
                    new_order.first_name = form.cleaned_data['first_name']
                    new_order.last_name = form.cleaned_data['last_name']
                    new_order.phone = form.cleaned_data['phone']
                    new_order.address = form.cleaned_data['email']
                    new_order.comment = form.cleaned_data['comment']
                    self.cart.in_order = True
                    new_order.cart = self.cart
                    new_order.save()
                    self.cart.save()
                    response = send_mail(email, first_name, last_name, phone, comment, self.cart, new_order)
                    if self.album.spreadsheet:
                        row = order2list(new_order)
                        spread, sheet = parse(self.album.spreadsheet)
                        insert(spread, sheet, [row])

                    return JsonResponse({'cart_counter': 0, 'email': response, 'album': f'/albums/{album_slug}'},
                                        status=200)


class ChangeQty(CartMixin, View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            service = Service.objects.get(id=request.POST['service_id'])
            service.qty = Decimal(request.POST['qty'])
            service.save()
            cart_product = CartProduct.objects.get(id=request.POST['cart_product_id'])
            cart_product.save()
            recalc_cart(self.cart)
            return JsonResponse(
                {'cart_counter': 0,
                 'total_price': self.cart.final_price,
                 'cart_total_price': self.cart.total,
                 'final_price': cart_product.final_price
                 }, status=200)


class PrivacyPolice(LanguageMixin, View):

    def get(self, request, *args, **kwargs):
        context = {}
        context['lang'] = self.customer.lang
        context['privacy'] = True
        context['content'] = PrivacyPoliceModel.objects.all()

        if StaticImage.objects.count():
            context['images'] = StaticImage.objects.last()

        return render(request, 'privacy.html', context)