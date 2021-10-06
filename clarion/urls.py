from django.urls import path
from . import views

app_name = 'clarion'

urlpatterns = [
    path('', views.index, name='index'),

    path('category/<int:pk>/news', views.category_pages, name='category_pages'),
    path('category/<int:pk>', views.category_detail, name='category_detail'),
    path('page/<int:pk>/edit', views.page_edit, name='page_edit'),
    path('page/<int:pk>', views.page_detail, name='page_detail'),

    path('registration', views.registration, name='registration'),
    path('cabinet', views.cabinet, name='cabinet'),

    path('parse_category', views.parse_category, name='parse_category')
]
