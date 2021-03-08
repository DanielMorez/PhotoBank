from django.urls import path


from .views import AlbumShowView, TypeAlbumShowView,\
                    UploadFilesView, CartView, AddToCartView, \
                    DeleteFromCartView, CheckoutView, MakeOrderView,\
                    MainPageView, ChangeLang, ChangeQty

urlpatterns = [
    path('', MainPageView.as_view(), name='base'),
    path('upload_files/', UploadFilesView.as_view(), name='upload_files'),
    path('albums/<str:album_slug>/', AlbumShowView.as_view(), name='album_detail'),
    path('albums/<str:album_slug>/<type_of_photo>/', TypeAlbumShowView.as_view(), name='album'),
    path('cart/', CartView.as_view(), name='cart'),
    path('add/', AddToCartView.as_view(), name='add_to_cart'),
    path('remove/', DeleteFromCartView.as_view(), name='remove_from_cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('makeorder/', MakeOrderView.as_view(), name='make_order'),
    path('change_lang', ChangeLang.as_view(), name='change_lang'),
    path('change_qty/', ChangeQty.as_view(), name='change_qty')
]
