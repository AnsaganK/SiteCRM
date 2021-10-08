from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse

from .forms import ReviewForm, UserCreateForm, PageForm, UserForm, CategoryForm
from .models import Category, Page
from .tasks import parser_category, parser_pages


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

def get_popular_pages():
    return Page.objects.all().annotate(review_sum=Sum('reviews__stars')/Count('reviews')).order_by('-review_sum')[:4]

def get_commented_pages():
    return Page.objects.all().annotate(comment_count=Count('reviews')).order_by('-comment_count')[:4]

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
                                                          'popular_pages': get_popular_pages(),
                                                          'commented_pages': get_commented_pages(),
                                                          'related_pages': get_related_pages(),
                                                          })
    return redirect('clarion:index')


def subcategory_create(request, pk):
    parent_category = Category.objects.filter(pk=pk).first()
    if not parent_category:
        return redirect('clarion:index')
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.parent_category = parent_category
            messages.success(request, 'category created')
        else:
            show_form_errors(request, form.errors)
        return redirect(reverse('clarion:category_pages', args=[category.pk]))

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
        return redirect(reverse('clarion:page_detail', args=[page.id]))
    if page:
        return render(request, 'clarion/page/edit.html', {'page': page})
    return redirect('clarion:index')



def page_detail(request, pk):
    page = Page.objects.filter(pk=pk).first()
    if request.method == 'POST':
        if request.user.reviews.filter(user__reviews__in=page.reviews.all()):
            messages.success(request, 'Не более одного комментария')
            return redirect(reverse('clarion:page_detail', args=[pk]))
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
                                                        'popular_pages': get_popular_pages(),
                                                        'commented_pages': get_commented_pages(),
                                                        'related_pages': get_related_pages(),})


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