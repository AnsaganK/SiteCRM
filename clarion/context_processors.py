from datetime import datetime

from django.db.models import Count

from clarion.models import Category


def categories_context(request):
    categories = Category.objects.annotate(children_count=Count('children')).order_by('children_count').filter(parent_category=None).distinct()
    date = datetime.now()
    day = date.day
    month = date.month
    year = date.year
    today = f'{day}.{month}.{year}'
    return {'categories': categories, 'today': today}