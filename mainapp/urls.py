from django.urls import path


from .views import ShowLastCreatedAlbums, PhotoShowView, AlbumShowView, TypeAlbumShowView,\
                    UploadFilesView, AlbumShowTypePhotoView, CartView, AddToCartView, \
                    DeleteFromCartView, ChangeQTYView, CheckoutView, MakeOrderView

urlpatterns = [
    path('', ShowLastCreatedAlbums.as_view(), name='base'),
    path('albums/', ShowLastCreatedAlbums.as_view(), name='base'),
    path('upload_files/', UploadFilesView.as_view(),name='upload_files'),
    path('albums/<str:album_slug>/', AlbumShowView.as_view(), name='album_detail'),
    path('albums/<str:album_slug>/<type_of_photo>/', TypeAlbumShowView.as_view(), name='album'),
    path('albums/<str:album_slug>/<type_of_photo>/<str:photo_slug>/', AlbumShowTypePhotoView.as_view(), name='product_detail'),
    path('cart/', CartView.as_view(), name='cart'),
    path('albums/<str:album_slug>/<type_of_photo>/<str:photo_slug>/add', AddToCartView.as_view(), name='add_to_cart'),
    path('albums/<str:album_slug>/<type_of_photo>/<str:photo_slug>/remove', DeleteFromCartView.as_view(), name='remove_from_cart'),
    path('cart/<str:photo_slug>/change', ChangeQTYView.as_view(), name='change_qty'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('makeorder/', MakeOrderView.as_view(), name='make_order')
]
