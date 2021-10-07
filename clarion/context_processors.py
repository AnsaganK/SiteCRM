from datetime import datetime

from django.db.models import Count, Sum

from clarion.models import Category, Page


def categories_context(request):
    categories = Category.objects.annotate(children_count=Count('children')).order_by('children_count').filter(parent_category=None).distinct()

    top_pages = Page.objects.all().annotate(review_sum=Sum('reviews__stars')/Count('reviews')).order_by('-review_sum')[:3]

    date = datetime.now()
    day = date.day
    month = date.month
    year = date.year
    today = f'{day}.{month}.{year}'
    return {'categories': categories,
            'today': today,
            'top_pages': top_pages}