# Generated by Django 3.1.4 on 2021-02-03 22:39

from django.db import migrations, models
import mainapp.models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0028_photo_selling_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='image',
            field=models.ImageField(upload_to=mainapp.models.get_upload_to, verbose_name='Фотография с водянным знаком'),
        ),
        migrations.AlterField(
            model_name='review',
            name='company',
            field=models.CharField(blank=True, max_length=512, null=True, verbose_name='Школа'),
        ),
        migrations.AlterField(
            model_name='watermark',
            name='image',
            field=models.ImageField(upload_to='watermarks'),
        ),
    ]