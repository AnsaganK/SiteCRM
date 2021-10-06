# Generated by Django 3.2.7 on 2021-10-06 11:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clarion', '0004_alter_category_base_page'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='parent_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='clarion.category', verbose_name='Родительская категория'),
        ),
    ]
