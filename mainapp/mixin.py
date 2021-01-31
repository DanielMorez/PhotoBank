from django.views.generic.detail import SingleObjectMixin
from django.views.generic import TemplateView

from .models import Album, Photo, PhotoType, Cart, Customer

class LanguageMixin(TemplateView):

    def dispatch(self, request, *args, **kwargs):
        try:
            self.customer = Customer.objects.get(user=request.user)
        except:
            if not request.session.session_key:
                request.session.save()
            device = request.session.session_key
            self.customer, created = Customer.objects.get_or_create(device=device)

        return super().dispatch(request, *args, **kwargs)


class CartMixin(TemplateView):

    def dispatch(self, request, *args, **kwargs):
        try:
            self.customer = Customer.objects.get(user=request.user)
        except:
            if not request.session.session_key:
                request.session.save()
            device = request.session.session_key
            self.customer, created = Customer.objects.get_or_create(device=device)

        self.cart, created = Cart.objects.get_or_create(owner=self.customer)
        self.products_id = [item.content_object.id for item in self.cart.related_products.all()]
        return super().dispatch(request, *args, **kwargs)

class AlbumsDetailMixin(SingleObjectMixin):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['albums'] = Album.objects.all()
        if self.kwargs.get('type_of_photo'):
            print(self.kwargs['type_of_photo'])
            album = Album.objects.get(slug=self.kwargs['album_slug'])
            photo_type = PhotoType.objects.get(type_of_photo=self.kwargs['type_of_photo'])
            context['photo_type'] = photo_type
            context['photos'] = Photo.objects.filter(album=album, type_of_photo=photo_type)

        return context
