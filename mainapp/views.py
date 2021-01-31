from django.contrib.contenttypes.models import ContentType
from django.views.generic import DetailView, TemplateView, FormView, View

from django.http import JsonResponse, HttpResponse

from django.db import transaction

from django.contrib import messages

from django.shortcuts import render
from .models import Cart, CartProduct
from django.http import HttpResponseRedirect

from .mixin import AlbumsDetailMixin, CartMixin, LanguageMixin

from .utils import recalc_cart

from .models import Photo, Album, PhotoType, Watermark, Customer
from .forms import PackageUploadFiles, OrderForm, CartForm

from .model_static import RusLang, EstLang, StaticImage, Review, \
                        Media, Portfolio, ServiceAndPrice



class MainPageView(LanguageMixin, TemplateView):

    template_name = 'base.html'
    lang_models = {
        'rus': RusLang,
        'est': EstLang
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lang'] = self.customer.lang
        lang_model = self.lang_models.get(self.customer.lang)
        if lang_model:
            if lang_model.objects.count():
                context['lang_dict'] = lang_model.objects.last();

        if StaticImage.objects.count():
            context['images'] = StaticImage.objects.last()

        context['reviews'] = Review.objects.all()
        context['portfolio'] = Portfolio.objects.all()
        if Review.objects.count():
            context['media'] = Media.objects.last()

        context['categories'] = set(item.type_of_photo for item in context['portfolio'])
        context['services'] = ServiceAndPrice.objects.all()

        return context

class ChangeLang(MainPageView):

    template_name = 'base.html'

    @transaction.atomic
    def get(self, request, *args, **kwargs):
        if self.customer.lang == 'rus':
            self.customer.lang = 'est'
        else:
            self.customer.lang = 'rus'
        self.customer.save()
        return HttpResponseRedirect('/')


class ShowLastCreatedAlbums(TemplateView):

    template_name = 'base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['language'] = RusLanguage.objects.first()
        return context

class AlbumShowView(CartMixin, TemplateView):

    template_name = 'album_detail.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['lang'] = self.customer.lang
        context['cart_counter'] = self.cart.products.count()

        context['albums'] = list(Album.objects.all())
        context['albums'].reverse()
        context['album'] = Album.objects.get(slug=kwargs['album_slug'])
        context['photo'] = list(Photo.objects.filter(album=context['album']))
        context['photo_types'] = set(photo.type_of_photo for photo in context['photo'])
        context['photo_types'] = [[t, Photo.objects.filter(type_of_photo=t).first()] for t in context['photo_types']]
        return context

class TypeAlbumShowView(AlbumsDetailMixin, DetailView):
    template_name = 'album.html'
    slug_url_kwarg = 'album_slug'

    def dispatch(self, request, *args, **kwargs):
        self.model = Album
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            customer = Customer.objects.get(user=self.request.user)
        except:
            device = self.request.COOKIES['csrftoken']
            customer, created = Customer.objects.get_or_create(device=device)
        cart, created = Cart.objects.get_or_create(owner=customer)
        context['cart_counter'] = cart.products.count()
        if cart:
            context['cart'] = cart
        context['products_id'] = [item.content_object.id for item in cart.related_products.all()]
        return context


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
    success_url = '/albums/'

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('files')

        if form.is_valid() and 'image' in request.FILES['files'].content_type:
            album = Album.objects.get(pk=request.POST['albums'])
            watermark = Watermark.objects.get(pk=request.POST['watermarks'])
            photo_type = PhotoType.objects.get(pk=request.POST['photo_type'])
            price = request.POST['price']
            for file in files:
                one_image = Photo(
                    album=album, title=file.name,
                    slug='photo_a', image=file,
                    price=price, type_of_photo=photo_type,
                    watermark=watermark
                )
                one_image.save()

            return self.form_valid(form)
        else:
            return self.form_invalid(form)

class AddToCartView(View):

    # @transaction.atomic
    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            try:
                self.customer = Customer.objects.get(user=request.user)
            except:
                if not request.session.session_key:
                    request.session.save()
                device = request.session.session_key
                self.customer, created = Customer.objects.get_or_create(device=device)

            self.cart, created = Cart.objects.get_or_create(owner=self.customer)
            self.products_id = [item.id for item in self.cart.related_products.all()]

            content_type = ContentType.objects.get_for_model(Photo)
            content_object = Photo.objects.get(slug=request.POST['photo_slug'])
            cart_product, created = CartProduct.objects.get_or_create(
                user=self.customer, cart=self.cart, content_type=content_type, object_id=content_object.id
            )

            self.cart.products.add(cart_product)
            recalc_cart(self.cart)
            return JsonResponse({'cart_counter': self.cart.products.count(), 'action': '/remove/', }, status=200)


class CartView(TemplateView):

    template_view = 'cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        try:
            customer = Customer.objects.get(user=self.request.user)
        except:
            device = self.request.COOKIES['csrftoken']
            customer, created = Customer.objects.get_or_create(device=device)
        cart, created = Cart.objects.get_or_create(owner=customer)
        context['cart'] = cart
        context['album'] = cart.related_products.first().content_object.album
        return context

    def get(self, request):
        try:
            customer = Customer.objects.get(user=request.user)
        except:
            device = self.request.COOKIES['csrftoken']
            customer, created = Customer.objects.get_or_create(device=device)
        cart, created = Cart.objects.get_or_create(owner=customer)
        album = cart.related_products.first().content_object.album

        return render(request, 'cart.html', {'cart': cart, 'album': album})

class CheckoutView(View):

    def get(self, request, *args, **kwargs):
        try:
            customer = Customer.objects.get(user=self.request.user)
        except:
            device = self.request.COOKIES['csrftoken']
            customer, created = Customer.objects.get_or_create(device=device)

        cart, created = Cart.objects.get_or_create(owner=customer)
        form = OrderForm(request.POST or None)
        albums = Album.reversed_objects()
        context = {
            'cart': cart,
            'albums': albums,
            'form': form
        }

        return render(request, 'checkout.html', context)

class DeleteFromCartView(CartMixin, TemplateView):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            content_type = ContentType.objects.get_for_model(Photo)
            content_object = Photo.objects.get(slug=request.POST['photo_slug'])
            cart_product, created = CartProduct.objects.get_or_create(
                user=self.customer, cart=self.cart, content_type=content_type, object_id=content_object.id
            )
            self.cart.products.remove(cart_product)
            recalc_cart(self.cart)
            cart_product.delete()
            print(self.cart.products.count())
            return JsonResponse({'cart_counter': self.cart.products.count(), 'action': '/add/'}, status=200)

    def get(self, request, *args, **kwargs):
        try:
            customer = Customer.objects.get(user=self.request.user)
        except:
            device = self.request.COOKIES['csrftoken']
            customer, created = Customer.objects.get_or_create(device=device)

        cart, created = Cart.objects.get_or_create(owner=customer)
        content_type = ContentType.objects.get_for_model(Photo)

        content_object = Photo.objects.get(slug=kwargs['photo_slug'])
        cart_product = CartProduct.objects.get(
            user=customer, cart=cart, content_type=content_type, object_id=content_object.id
        )
        cart.products.remove(cart_product)
        recalc_cart(self.cart)
        return HttpResponseRedirect('/cart/')

class ChangeQTYView(CartMixin, TemplateView):

    def post(self, request, *args, **kwargs):
        try:
            customer = Customer.objects.get(user=self.request.user)
        except:
            device = self.request.COOKIES['csrftoken']
            customer, created = Customer.objects.get_or_create(device=device)

        cart, created = Cart.objects.get_or_create(owner=customer)
        content_type = ContentType.objects.get_for_model(Photo)

        content_object = Photo.objects.get(slug=kwargs['photo_slug'])
        cart_product = CartProduct.objects.get(
            user=customer, cart=cart, content_type=content_type, object_id=content_object.id
        )
        qty = int(request.POST.get('qty'))
        cart_product.qty = qty
        cart_product.save()
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, "Кол-во успешно изменено добавлен")
        return HttpResponseRedirect('/cart/')


class MakeOrderView(CartMixin, TemplateView):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        if form.is_valid():
            new_order = form.save(commit=False)
            try:
                customer = Customer.objects.get(user=self.request.user)
            except:
                device = self.request.COOKIES['csrftoken']
                customer, created = Customer.objects.get_or_create(device=device)
            new_order.customer = customer
            new_order.first_name = form.cleaned_data['first_name']
            new_order.last_name = form.cleaned_data['last_name']
            new_order.phone = form.cleaned_data['phone']
            new_order.address = form.cleaned_data['address']
            new_order.buying_type = form.cleaned_data['buying_type']
            new_order.order_date = form.cleaned_data['order_date']
            new_order.comment = form.cleaned_data['comment']
            new_order.save()
            customer.orders.add(new_order)
            self.cart.in_order = True
            self.cart.save()
            messages.add_message(request, messages.INFO, 'Спасибо за заказ! Письмо с заказом было отправленно к вам на потчу.')
            return HttpResponseRedirect('/')
        return HttpResponseRedirect('/checkout/')
