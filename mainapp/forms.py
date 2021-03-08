from django import forms

from .models import Album, Watermark, PhotoType, Order, Cart


PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 5)]


class PackageUploadFiles(forms.Form):

    albums = forms.ModelChoiceField(label='Альбом', queryset=Album.objects.all(), required=True)
    photo_type = forms.ModelChoiceField(label='Тип фотографий', queryset=PhotoType.objects.all(), required=True)
    files = forms.FileField(label='Фотографии', widget=forms.ClearableFileInput(attrs={'multiple': True}), required=True)
    watermarks = forms.ModelChoiceField(label='Водяной знак', queryset=Watermark.objects.all(), required=False)


class CartForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = '__all__'


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = (
            'first_name', 'last_name', 'phone', 'email', 'comment'
        )
