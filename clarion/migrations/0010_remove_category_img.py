# Generated by Django 3.2.7 on 2021-10-07 10:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clarion', '0009_auto_20211007_1135'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='img',
        ),
    ]
