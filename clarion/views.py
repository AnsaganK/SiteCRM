import requests
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count, Sum, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse

from constants import admin_username, parser_host
from .forms import ReviewForm, UserCreateForm, PageForm, UserForm, CategoryForm
from .models import Category, Page
from .tasks import parser_category, parser_pages, update_page, check_pages, base_url


def show_form_errors(request, errors):
    for error in errors:
        messages.error(request, errors[error])



def category_tree(category, zero=1):
    zero += 1
    categories_list = []
    category_children = category.children.all()
    for category_child in category_children:
        tree = category_tree(category_child, zero)
        categories_list.append({'category': category_child.name, 'children': tree})
    return categories_list


def show_categories(categories):
    categories_list = []
    for category in categories:
        if category.children:
            tree = category_tree(category)
            categories_list.append({'category': category.name, 'children': tree})
    return categories_list


def parse_pages(request):
    Page.objects.filter(isCategory=None).filter(is_created=False).delete()
    parser_pages.delay()
    messages.success(request, 'Парсинг начат')
    return redirect('clarion:index')


def parse_category(request):
    Category.objects.all().delete()
    Page.objects.all().delete()
    parser_category.delay()
    messages.success(request, 'Парсинг начат')
    return redirect('clarion:index')



def index(request):
    last_pages = Page.objects.all().order_by('-pk')[:3]

    # categories = show_categories(Category.objects.filter(parent_category=None))
    return render(request, 'clarion/index.html', {'last_pages': last_pages})


def get_popular_pages(limit=None):
    pages = Page.objects.annotate(review_sum=Sum('reviews__stars')/Count('reviews')).order_by('review_sum')
    if limit:
        return pages[:limit]
    return pages

def get_commented_pages(limit=None):
    pages = Page.objects.all().annotate(comment_count=Count('reviews')).order_by('-comment_count')
    if limit:
        return pages[:limit]
    return pages

def get_related_pages():
    return Page.objects.all()[:4]


def category_pages(request, pk):
    category = Category.objects.filter(pk=pk).first()
    if category:
        pages = category.pages.all()
        paginator = Paginator(pages, 10)
        page = request.GET.get('page')
        try:
            pages = paginator.page(page)
        except PageNotAnInteger:
            pages = paginator.page(1)
        except EmptyPage:
            pages = paginator.page(paginator.num_pages)
        return render(request, 'clarion/page/list.html', {'category': category, 'pages': pages,
                                                          'popular_pages': get_popular_pages(limit=4),
                                                          'commented_pages': get_commented_pages(limit=4),
                                                          'related_pages': get_related_pages(),
                                                          })
    return redirect('clarion:index')

def category_edit(request, pk):
    category = Category.objects.filter(pk=pk).first()
    if not category:
        return redirect('clarion:index')
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            messages.success(request, 'Категория изменена')
            form.save()
        else:
            show_form_errors(request, form.errors)
        return redirect(reverse('clarion:category_pages', args=[category.pk]))
    return render(request, 'clarion/category/edit.html', {'category': category})


def subcategory_create(request, pk):
    parent_category = Category.objects.filter(pk=pk).first()
    if not parent_category:
        return redirect('clarion:index')
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.parent_category = parent_category
            category.save()
            messages.success(request, 'category created')
        else:
            show_form_errors(request, form.errors)
        return redirect(reverse('clarion:category_pages', args=[parent_category.pk]))
    return render(request, 'clarion/category/subcategory/create.html')


def save_page_form(post, files):
    pass


def base_page_create(request, pk):
    pass


def page_create(request, pk):
    category = Category.objects.filter(pk=pk).first()
    if not category:
        return redirect('clarion:index')

    if request.method == 'POST':
        form = PageForm(request.POST, request.FILES)
        if form.is_valid():
            page = form.save(commit=False)
            page.is_created = True
            page.category = category
            page.save()
            messages.success(request, f'Страница {page.name} создана')
            return redirect(reverse('clarion:category_pages', args=[category.pk]))
        else:
            show_form_errors(form.errors)
    return render(request, 'clarion/page/create.html')


@login_required()
def page_delete_confirm(request, pk):
    page = Page.objects.filter(pk=pk).first()
    if page:
        page.delete()
    return redirect('clarion:index')

@login_required()
def page_delete(request, pk):
    page = Page.objects.filter(pk=pk).first()
    if not page:
        return redirect('clarion:index')
    return render(request, 'clarion/page/delete_confirm.html', {'page': page})

@login_required()
def page_edit(request, pk):
    page = Page.objects.filter(pk=pk).first()
    if request.method == 'POST':
        form = PageForm(request.POST, request.FILES, instance=page)
        if form.is_valid():
            form.save()
        else:
            show_form_errors(request, form.errors)
        return redirect(page.get_absolute_url())
    if page:
        return render(request, 'clarion/page/edit.html', {'page': page})
    return redirect('clarion:index')

def page_update(request, pk):
    page = Page.objects.filter(pk=pk).first()
    if not page or not page.url:
        return redirect('clarion:index')
    update_page.delay(pk=pk, url=page.url)
    messages.success(request, 'Данные скоро изменятся, обновите страницу')
    return redirect(reverse('clarion:page_detail', args=[page.pk]))

def page_detail_pk(request, pk):
    page = Page.objects.filter(pk=pk).first()
    if not page:
        return render(request, '404.html')
    return render(request, 'clarion/page/detail.html', {'page': page,
                                                        'popular_pages': get_popular_pages(limit=4),
                                                        'commented_pages': get_commented_pages(limit=4),
                                                        'related_pages': get_related_pages(),})

def page_detail(request, url):
    print(base_url+url)
    page = Page.objects.filter(url=base_url+'/'+url).first()
    if not page:
        return render(request, '404.html')
    print(page)
    if request.method == 'POST':
        if request.user.reviews.filter(user__reviews__in=page.reviews.all()):
            messages.success(request, 'Не более одного комментария')
            return redirect(reverse('clarion:page_detail', args=[url]))
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.page = page
            review.save()
            messages.success(request, 'Ваш отзыв сохранен')
        else:
            print(form.errors)
            show_form_errors(request, form.errors)
        return redirect(page.get_absolute_url())
    return render(request, 'clarion/page/detail.html', {'page': page,
                                                        'popular_pages': get_popular_pages(limit=4),
                                                        'commented_pages': get_commented_pages(limit=4),
                                                        'related_pages': get_related_pages(),})

def popular_pages(request):
    title = 'Top popular pages'
    pages = get_popular_pages()
    paginator = Paginator(pages, 12)
    page = request.GET.get('page')
    try:
        pages = paginator.page(page)
    except PageNotAnInteger:
        pages = paginator.page(1)
    except EmptyPage:
        pages = paginator.page(paginator.num_pages)
    return render(request, 'clarion/page/top_list.html', {'title': title, 'pages': pages})


def commented_pages(request):
    title = 'Top commented pages'
    pages = get_commented_pages()
    paginator = Paginator(pages, 12)
    page = request.GET.get('page')
    try:
        pages = paginator.page(page)
    except PageNotAnInteger:
        pages = paginator.page(1)
    except EmptyPage:
        pages = paginator.page(paginator.num_pages)
    return render(request, 'clarion/page/top_list.html', {'title': title,'pages': pages})

def search(request):
    query = ''
    if request.method == 'GET':
        query = request.GET.get('search')
    pages = Page.objects.filter(
        Q(name__icontains=query) | Q(content__icontains=query)
    )
    search_count = pages.count()
    paginator = Paginator(pages, 12)
    page = request.GET.get('page')
    try:
        pages = paginator.page(page)
    except PageNotAnInteger:
        pages = paginator.page(1)
    except EmptyPage:
        pages = paginator.page(paginator.num_pages)
    return render(request, 'clarion/page/search.html', {'pages': pages, 'query': query, 'search_count': search_count})


def registration(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse('clarion:index'))
        else:
            show_form_errors(request, form.errors)
    return render(request, 'registration/registration.html')


def cabinet(request):
    user = request.user
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            messages.success(request, 'Данные успешно обновлены')
            form.save()
        else:
            show_form_errors(request, form.errors)
    return render(request, 'registration/cabinet.html', {'user': user})


def check_page_links(request):
    #Page.objects.exclude(category=None).delete()
    messages.success(request, 'Исправление ссылок начинается')
    check_pages.delay()
    return redirect('clarion:index')



# GoogleParser
def my_queries(request, id):
    username = admin_username

def my_place(request, id):
    username = admin_username


def start_parser(username, query_name, query_page):
    url = parser_host + f'query/add?username={username}&query_name={query_name}&query_page={query_page}'
    r = requests.get(url)
    if r.status_code == 200:
        try:
            return r.json()['message']
        except:
            pass
    return "Ошибка"


def query_add(request):
    username = admin_username
    if request.method == 'POST':
        post = request.POST
        query_name = post['query_name']
        try:
            not_all = post['not_all']
        except:
            not_all = None
        if not_all:
            try:
                query_page = request.POST['query_page']
                query_page = int(query_page)
            except:
                query_page = 1
        else:
            query_page = 0

        start = start_parser(username, query_name, query_page)
        messages.success(request, start)
        print(query_name)
        print(not_all)
        print(query_page)
        return redirect('clarion:query_add')
    return render(request, 'clarion/parser/form.html')

def get_queries(url):
    queries = []
    r = requests.get(url)
    if r.status_code == 200:
        try:
            queries = r.json()
        except:
            queries = []
    return queries


def query_my(request):
    username = admin_username
    url = parser_host + f'query/{username}'
    print(url)
    queries = get_queries(url)
    return render(request, 'clarion/parser/my.html', {'queries': queries})


def get_places(url):
    places = {}
    r = requests.get(url)
    if r.status_code == 200:
        try:
            places = r.json()['places']
            letters = r.json()['letters']
            places_letter = r.json()['places_letter']
            places = {
                'places': places,
                'letters': letters,
                'places_letter': places_letter,
            }
            return places
        except:
            places = {}
    return places


def query_places(request, slug):
    username = admin_username
    url = parser_host + f'query/{slug}/places'
    print(url)
    data = get_places(url)
    print(data)
    places = data['places'] if 'places' in data else []
    letters = data['letters'] if 'letters' in data else []
    places_letter = data['places_letter'] if 'places_letter' in data else []
    return render(request, 'clarion/parser/places.html', {'places': places,
                                                          'letters': letters,
                                                          'places_letter': places_letter
                                                          })


def get_place(url):
    place = {}
    r = requests.get(url)
    if r.status_code == 200:
        try:
            place = r.json()
        except:
            place = []
    return place


def place_detail(reqeust, slug):
    url = parser_host + f'place/{slug}'
    print(url)
    place = get_place(url)
    return render(reqeust, 'clarion/parser/place.html', {'place': place})