from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse

from .forms import ReviewForm, UserCreateForm
from .models import Category, Page
from .tasks import parser_clarion


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



def index(request):
    # categories = show_categories(Category.objects.filter(parent_category=None))
    return render(request, 'clarion/index.html',)


def category_detail(request, pk):
    category = Category.objects.filter(pk=pk).first()
    if category and category.base_page:
        page = category.base_page
        print(page)
        return redirect(reverse('clarion:page_detail', args=[page.id]))
    return redirect('clarion:index')


def page_detail(request, pk):
    page = Page.objects.filter(pk=pk).first()
    if request.method == 'POST':
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
    popular_pages = Page.objects.all()[:4]
    commented_pages = Page.objects.all().annotate(comment_count=Count('reviews')).order_by('-comment_count')[:4]
    related_pages = Page.objects.all()[:4]
    return render(request, 'clarion/page/detail.html', {'page': page, 'popular_pages': popular_pages,
                                                        'commented_pages': commented_pages, 'related_pages': related_pages,
                                                        })

def parse_category(request):
    Category.objects.all().delete()
    Page.objects.all().delete()
    parser_clarion.delay()
    messages.success(request, 'Парсинг начат')
    return redirect('clarion:index')


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
    return render(request, 'registration/cabinet.html', {'user': user})