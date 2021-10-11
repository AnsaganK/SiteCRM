from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.shortcuts import reverse


class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    parent_category = models.ForeignKey('Category', null=True, blank=True, on_delete=models.CASCADE, related_name='children', verbose_name='Родительская категория')
    base_page = models.ForeignKey('Page', null=True, blank=True, on_delete=models.CASCADE, related_name='isCategory', verbose_name='Страница')

    date_create = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    date_update = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f'{self.name} | {self.parent_category.name if self.parent_category else "-"}'

    def get_absolute_url(self):
        return reverse('clarion:category_pages', args=[self.id])

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['pk']


class Page(models.Model):
    img = models.ImageField(upload_to='pages', null=True, blank=True, verbose_name='Картинка')

    name = models.CharField(max_length=400, verbose_name='Название')
    url = models.URLField(max_length=1000, null=True, blank=True, verbose_name='Ссылка')

    content = models.TextField(null=True, blank=True, verbose_name='Контент')
    html = models.TextField(null=True, blank=True, verbose_name='HTML страницы')

    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE, related_name='pages', verbose_name='Категория')

    is_created = models.BooleanField(default=False)

    date_create = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    date_update = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    def get_absolute_url(self):
        return reverse('clarion:page_detail', args=[self.id])

    def get_rating(self):
        if self.reviews.count():
            reviews__stars__sum = self.__class__.objects.filter(reviews__page=self).aggregate(Sum('reviews__stars'))
            reviews__stars__count = self.reviews.count()
            rating = reviews__stars__sum['reviews__stars__sum']/reviews__stars__count
            return rating
        return 0


    class Meta:
        verbose_name = 'Страница'
        verbose_name_plural = 'Страницы'
        ordering = ['-pk']


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='reviews')
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    stars_choices = ((i, i) for i in range(1, 6))
    stars = models.IntegerField(max_length=100, default=5, choices=stars_choices)

    def __str__(self):
        return self.id

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-pk']

