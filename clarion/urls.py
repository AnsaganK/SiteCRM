from django.conf.urls import url
from django.urls import path, re_path
from . import views

app_name = 'clarion'



urlpatterns = [
    path('', views.index, name='index'),
    path('category/<int:pk>/edit', views.category_edit, name='category_edit'),
    path('category/<int:pk>/news', views.category_pages, name='category_pages'),
    path('category/<int:pk>/subcategory/create', views.subcategory_create, name='subcategory_create'),
    path('category/<int:pk>/page/base/create', views.base_page_create, name='base_page_create'),
    path('category/<int:pk>/page/create', views.page_create, name='page_create'),
    # path('category/<int:pk>', views.category_detail, name='category_detail'),


    path('registration', views.registration, name='registration'),
    path('cabinet', views.cabinet, name='cabinet'),

    path('parse/pages', views.parse_pages, name='parse_pages'),
    path('parse/category', views.parse_category, name='parse_category'),

    path('check_page_links', views.check_page_links, name='check_page_links'),

    path('page/search/', views.search, name='search'),
    path('page/commented/', views.commented_pages, name='commented_pages'),
    path('page/rating/', views.popular_pages, name='popular_pages'),
    path('page/search/', views.search, name='search'),
    path('page/<int:pk>/detail', views.page_detail_pk, name='page_detail_pk'),
    path('page/<int:pk>/update', views.page_update, name='page_update'),
    path('page/<int:pk>/edit', views.page_edit, name='page_edit'),
    path('page/<int:pk>/delete/confirm', views.page_delete_confirm, name='page_delete_confirm'),
    path('page/<int:pk>/delete/', views.page_delete, name='page_delete'),
]

urlpatterns += [
    path('query/add', views.query_add, name="query_add"),
    path('query/my', views.query_my, name="query_my"),
    path('query/', views.query_add, name="query"),
]

urlpatterns += [
    path('<path:url>', views.page_detail, name='page_detail'),
]