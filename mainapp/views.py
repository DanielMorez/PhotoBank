from django.contrib.contenttypes.models import ContentType
from django.views.generic import DetailView, TemplateView, FormView, View

from django.db import transaction

from django.contrib import messages

from django.shortcuts import render
from .models import Cart, CartProduct
from django.http import HttpResponseRedirect

from .mixin import AlbumsDetailMixin, CartMixin

from .utils import recalc_cart

from .models import Photo, Album, PhotoType, Watermark, Customer
from .forms import PackageUploadFiles, OrderForm


class ShowLastCreatedAlbums(TemplateView):

    template_name = 'base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['albums'] = list(Album.objects.all())
        context['albums'].reverse()
        return context

class AlbumShowView(CartMixin, TemplateView):

    template_name = 'album_detail.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['cart'] = self.cart
        context['albums'] = list(Album.objects.all())
        context['albums'].reverse()
        context['album'] = Album.objects.get(slug=kwargs['album_slug'])
        context['photo'] = list(Photo.objects.filter(album=context['album']))
        context['photo_types'] = set(photo.type_of_photo for photo in context['photo'])
        print(context['photo_types'])
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
        if cart:
            context['cart'] = cart
        return context


class AlbumShowTypePhotoView(TemplateView):

    template_name = 'product_detail.html'
    success_url = '/albums/'

    def get_context_data(self, **kwargs):
        print(kwargs)
        print(self.request.session)

        context = super().get_context_data(**kwargs)
        context['album'] = Album.objects.get(slug=kwargs['album_slug'])
        context['photo_type'] = PhotoType.objects.get(type_of_photo=kwargs['type_of_photo'])
        context['photo'] = Photo.objects.get(slug=kwargs['photo_slug'])
        return context


class PhotoShowView(TemplateView):

    template_name = 'product_detail.html'
    slug_url_kwarg = 'slug'

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


class AddToCartView(CartMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        try:
            customer = Customer.objects.get(user=self.request.user)
        except:
            device = self.request.COOKIES['csrftoken']
            customer, created = Customer.objects.get_or_create(device=device)

        cart, created = Cart.objects.get_or_create(owner=customer)
        content_type = ContentType.objects.get_for_model(Photo)

        content_object = Photo.objects.get(slug=kwargs['photo_slug'])
        cart_product, created = CartProduct.objects.get_or_create(
            user=customer, cart=cart, content_type=content_type, object_id=content_object.id
        )

        cart.products.add(cart_product)
        recalc_cart(self.cart)
        return HttpResponseRedirect('..')


class CartView(View):

    def get(self, request, *args, **kwargs):
        try:
            customer = Customer.objects.get(user=self.request.user)
        except:
            device = self.request.COOKIES['csrftoken']
            customer, created = Customer.objects.get_or_create(device=device)

        cart, created = Cart.objects.get_or_create(owner=customer)

        albums = Album.reversed_objects()
        context = {
            'cart': cart,
            'albums': albums
        }

        return render(request, 'cart.html', context)


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
