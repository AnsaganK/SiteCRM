from io import BytesIO

from celery import shared_task

import requests
from bs4 import BeautifulSoup as BS
from django.core import files
from django.core.files.base import ContentFile

from clarion.models import Category, Page



base_url = 'https://clarionherald.info'
url2 = 'https://clarionherald.info/clarion/index.php/news'

PAGES = []
EQUAL_COUNT = 0

def get_site(url=base_url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.text
    return None


def get_soup(response_text):
    html = BS(response_text, 'lxml')
    return html

# Перевод ссылок на данный сайт
def create_or_get_page(name, url):
    if Page.objects.filter(url=url).first():
        #print('Такая страница есть в базе')
        return Page.objects.filter(url=url).first()
    #print('Такой страницы нет в базе, жалко')
    page = detail_page(name, url)
    check_page(page.pk)
    return page


def check_links(html):
    links = html.find_all('a')
    locale_links_count = 0
    #print(f'В этой странице найдено {len(links)} ссылок')
    for link_index in range(len(links)):
        link = links[link_index]
        if ('/' == link['href'][0]) and ('/page' != link['href'][:5] or ('/clarion' in link['href'] or '.php' in link['href'])):
            locale_links_count += 1
            name = link['href'].split('/')[-1]
            page = create_or_get_page(name, base_url+link['href'])
            link['href'] = page.get_absolute_url()
            links[link_index].replace_with = link
    #print(f'Из них локальных {locale_links_count}')
    #print()
    return str(links)


def check_page(page_pk):
    page = Page.objects.filter(pk=page_pk).first()
    content = get_soup(page.content)
    page.content = check_links(content)
    page.save()


@shared_task
def check_pages():
    pages = Page.objects.exclude(url=None)
    print(f'Всего страниц {pages.count()}')
    for page in pages:
        print(f'Сейчас проверяю страницу {page.pk}: {page.name}')
        check_page(page.pk)
    return 'Исправление ссылок сделано'


# Парсер страниц с главной страницы
def get_category(name):
    category = Category.objects.filter(name=name).first()
    return category if category else None

@shared_task
def update_page(pk, url):
    page = Page.objects.filter(pk=pk).first()
    if not page:
        return None
    site = get_soup(get_site(url))
    content = site.find_all('div', class_='art-post-inner')[-1]
    page.content = str(content)
    page.save()
    return f' Страница {page.name} обновлена'


def detail_page(name, url):
    site = get_soup(get_site(url))
    if not site:
        return site
    try:
        content = site.find_all('div', class_='art-post-inner')[-1]
    except:
        content = ''
        return create_page(name=name, html_dict={
            'html': str(site),
            'content': str(content)
        }, url=url)

    html_dict = {
            'html': str(site),
            'content': str(content)
        }



    try:
        category_name = site.find('span', class_='art-post-metadata-category-parent').text
        category = get_category(name=category_name)
    except:
        category = None
    try:
        picture_element = content.find('div', class_='art-article')
        if picture_element.find('img'):
            img_url = picture_element.find('img')['src']
        else:
            img_url = picture_element.find('input')['src']
        img_url = base_url + img_url
    except:
        img_url = None

    return create_page(name=name, html_dict=html_dict, url=url, category=category, img_url=img_url)



def get_pages_link(cards):
    global PAGES
    global EQUAL_COUNT
    paginate_block = cards[-1]
    next_link = paginate_block.find('li', 'pagination-next').find('a')['href']

    for i in cards[:-1]:
        title = i.find('h2', class_='art-postheader').text
        try:
            link = i.find('a', class_='readon art-button')['href']
        except:
            link = None
        page_object = {
            'title': title,
            'link': link
        }
        if page_object in PAGES:
            EQUAL_COUNT += 1
        else:
            if link:
                detail_page(name=title, url=base_url+link)
            PAGES.append(page_object)
    return next_link


def parser_page_recursion(url):
    print()
    html = get_soup(get_site(url))
    cards = html.find('div', class_='blog-featured').findChildren(recursive=False)
    next_link = get_pages_link(cards)
    if next_link and EQUAL_COUNT < 100:
        parser_pages(base_url + next_link)
    else:
        print('Парсинг завершен')
        return 'Парсинг с главной страницы завершен'

@shared_task
def parser_pages(url=base_url):
    result = parser_page_recursion(url=url)
    global PAGES
    global EQUAL_COUNT
    PAGES = []
    EQUAL_COUNT = 0
    return result

@shared_task
def save_image_url(page_id, img_url):
    page = Page.objects.filter(pk=page_id).first()
    r = requests.get(img_url)
    if r.status_code == 200 and page:
        fp = BytesIO()
        fp.write(r.content)
        file_name = img_url.split('/')[-1]
        file = files.File(fp)
        if file.size > 1000:
            page.img.save(file_name, files.File(fp))
            return f'id: {page_id} url: {img_url} (Картинка сохранена)'

# Парсер категории меню
def create_page(name, html_dict=None, url=None, category=None, img_url=None):
    page = Page.objects.create(name=name)
    page.save()
    if url:
        page.url = url
    if html_dict:
        page.html = html_dict['html']
        page.content = html_dict['content']
    if category:
        page.category = category
        #page.is_created = True
    if img_url:
        save_image_url.delay(page_id=page.pk, img_url=img_url)
    page.save()
    return page


def create_category(category_name, category_link=None, parent_category=None):
    category = Category.objects.create(name=category_name)
    category.save()
    if category_link:
        html_dict = get_page(category_link)
        base_page = create_page(name=category_name, html_dict=html_dict, url=category_link)
        category.base_page = base_page
    if parent_category:
        category.parent_category = parent_category
    category.save()
    return category


def get_categories(categories, parent_category=None):
    for category in categories:
        category_tag = category.find('a')
        category_link = base_url + category_tag['href']
        category_name = category_tag.text
        new_category = create_category(category_name, category_link, parent_category)
        try:
            ul = category.find('ul')
            ul_categories = ul.findChildren(recursive=False)
            get_categories(ul_categories, new_category)
        except:
            pass


def get_page(page_url):
    site = get_site(page_url)
    soup = get_soup(site)
    try:
        content = soup.find('div', class_='art-post-body')
    except:
        content = ''
    return {
        'html': str(soup),
        'content': str(content)
    }

@shared_task
def parser_category():
    # return 'Success'
    site = get_site()
    soup = get_soup(site)
    menu = soup.find('ul', class_='art-hmenu')
    categories = menu.findChildren(recursive=False)
    get_categories(categories)
    return 'Парсинг категории завершен'


if __name__ == '__main__':
    check_pages()
