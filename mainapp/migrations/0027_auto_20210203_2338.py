# Generated by Django 3.1.4 on 2021-02-03 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0026_auto_20210203_2319'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='image',
            field=models.ImageField(upload_to='', verbose_name='Фотография с водянным знаком'),
        ),
    ]
