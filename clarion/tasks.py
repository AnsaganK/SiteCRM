from celery import shared_task

import requests
from bs4 import BeautifulSoup as BS
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

    content = site.find_all('div', class_='art-post-inner')[-1]
    try:
        category_name = site.find('span', class_='art-post-metadata-category-parent').text
        category = get_category(name=category_name)
    except:
        category = None

    html_dict = {
        'html': str(site),
        'content': str(content)
    }
    create_page(name=name, html_dict=html_dict, url=url, category=category)



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
        print(title, link)
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
        print(base_url + next_link)
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



# Парсер категории меню
def create_page(name, html_dict=None, url=None, category=None):
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
    parser_category()
