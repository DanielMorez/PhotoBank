# Generated by Django 3.1.4 on 2021-02-03 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0023_emailcredentials'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='address',
        ),
        migrations.AddField(
            model_name='order',
            name='email',
            field=models.CharField(blank=True, max_length=1024, null=True, verbose_name='Email'),
        ),
    ]