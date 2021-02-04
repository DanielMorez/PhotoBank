from django.views.generic.detail import SingleObjectMixin
from django.views.generic import View

from .model_static import RusLang, EstLang, StaticImage
from .models import Album, Photo, PhotoType, Cart, Customer

class LanguageMixin(View):

    lang_models = {
        'rus': RusLang,
        'est': EstLang
    }

    def dispatch(self, request, *args, **kwargs):
        try:
            self.customer = Customer.objects.get(user=request.user)
        except:
            if not request.session.session_key:
                request.session.save()
            device = request.session.session_key
            self.customer, created = Customer.objects.get_or_create(device=device)

        try:
            self.images = StaticImage.objects.last()
        except:
            self.images = None

        self.lang_model = self.lang_models.get(self.customer.lang)
        if self.lang_model:
            if self.lang_model.objects.count():
                self.lang_model = self.lang_model.objects.last();

        return super().dispatch(request, *args, **kwargs)


class CartMixin(View):

    def dispatch(self, request, *args, **kwargs):

        self.album = None
        self.type_of_photo = None
        self.products_id = None

        try:
            self.customer = Customer.objects.get(user=request.user)
        except:
            if not request.session.session_key:
                request.session.save()
            device = request.session.session_key
            self.customer, created = Customer.objects.get_or_create(device=device)

        if kwargs.get('album_slug'):
            self.album = Album.objects.get(slug=kwargs['album_slug'])
        if kwargs.get('type_of_photo'):
            self.type_of_photo = PhotoType.objects.get(type_of_photo=kwargs['type_of_photo'])

        self.cart, created = Cart.objects.get_or_create(owner=self.customer, in_order=False)
        if not self.album and self.cart.products.count():
            self.album = self.cart.products.last().content_object.album
            self.products_id = [item.content_object.id for item in self.cart.related_products.all()]
        return super().dispatch(request, *args, **kwargs)

