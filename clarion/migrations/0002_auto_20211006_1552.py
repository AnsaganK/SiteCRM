# Generated by Django 3.2.7 on 2021-10-06 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clarion', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='date_create',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='date_update',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='page',
            name='date_update',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='page',
            name='date_create',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
