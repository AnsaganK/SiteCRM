from django.contrib import admin
from .models import Category, Page, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_page']
    raw_id_fields = ['parent_category']

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']


admin.site.register(Review)