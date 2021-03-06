# Generated by Django 3.2.7 on 2021-10-06 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clarion', '0002_auto_20211006_1552'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='is_created',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='category',
            name='img',
            field=models.ImageField(blank=True, null=True, upload_to='category', verbose_name='Картинка'),
        ),
        migrations.AlterField(
            model_name='page',
            name='img',
            field=models.ImageField(blank=True, null=True, upload_to='pages', verbose_name='Картинка'),
        ),
        migrations.AlterField(
            model_name='page',
            name='url',
            field=models.URLField(blank=True, max_length=500, null=True, verbose_name='Ссылка'),
        ),
    ]
