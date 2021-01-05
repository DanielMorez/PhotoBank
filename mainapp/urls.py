from django.urls import path

from .views import ShowLastCreatedAlbums, PhotoShowView, AlbumShowView, TypeAlbumShowView

urlpatterns = [
    path('', ShowLastCreatedAlbums.as_view(), name='base'),
    path('albums/', ShowLastCreatedAlbums.as_view(), name='base'),
    path('albums/<str:album_slug>/', AlbumShowView.as_view(), name='choice_type_photo'),
    path('albums/<str:album_slug>/<type_of_photo>/', TypeAlbumShowView.as_view(), name='album'),
    path('albums/<str:album_slug>/<type_of_photo>/<str:photo_slug>/', PhotoShowView.as_view(), name='product_detail')
]
