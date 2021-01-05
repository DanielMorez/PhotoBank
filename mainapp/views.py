from django.shortcuts import render
from django.views.generic import DetailView, TemplateView

from .models import Photo, Album, PhotoType

class ShowLastCreatedAlbums(TemplateView):
    context_object_name = 'albums'
    template_name = 'base.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['albums'] = Album.objects.all()
        return context

class AlbumShowView(TemplateView):

    template_name = 'choice_type_photo.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['album'] = Album.objects.get(slug=kwargs['album_slug'])
        context['photo'] = list(Photo.objects.filter(album=context['album']))
        context['photo_types'] = set(photo.type_of_photo for photo in context['photo'])
        print(context['photo_types'])
        return context

class TypeAlbumShowView(TemplateView):
    template_name = 'album.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        print(kwargs)
        context = super().get_context_data(**kwargs)
        context['album'] = Album.objects.get(slug=kwargs['album_slug'])
        context['photo_type'] = PhotoType.objects.get(type_of_photo=kwargs['type_of_photo'])
        context['photos'] = list(Photo.objects.filter(
            album=context['album'],
            type_of_photo=context['photo_type']
        ))
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

