from django.db import models
from django.shortcuts import reverse


class Category(models.Model):
    img = models.ImageField(upload_to='category')
    name = models.CharField(max_length=200, verbose_name='Название')
    parent_category = models.ForeignKey('Category', on_delete=models.CASCADE, verbose_name='Родительская категория')
    page = models.ForeignKey('Page', on_delete=models.CASCADE, verbose_name='Страница')


    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', args=[self.id])

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = '-pk'


class Page(models.Model):
    img = models.ImageField(upload_to='pages')
    title = models.CharField(max_length=200, verbose_name='Название')
    url = models.URLField(max_length=500, verbose_name='Ссылка')
    content = models.TextField(verbose_name='Контент')
    html = models.TextField(verbose_name='HTML страницы')
    date_create = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.url

    def get_absolute_url(self):
        return reverse('page_detail', args=[self.id])

    class Meta:
        verbose_name = 'Страница'
        verbose_name_plural = 'Страницы'
        ordering = '-pk'