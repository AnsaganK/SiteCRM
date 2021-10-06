from celery import shared_task

import requests
from bs4 import BeautifulSoup as BS
from clarion.models import Category, Page

url = 'https://clarionherald.info'
url2 = 'https://clarionherald.info/clarion/index.php/news'


def get_site(url=url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.text
    return None


def get_soup(response_text):
    html = BS(response_text, 'lxml')
    return html


def create_page(name, html_dict=None, url=None, category=None):
    page = Page.objects.create(name=name)
    page.save()
    if url:
        page.url = url
    if html_dict:
        page.html = str(html_dict['html'])
        page.content = str(html_dict['content'])
    if category:
        page.category = category
        page.is_created = True
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
        category_link = url + category_tag['href']
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
        'html': soup,
        'content': content
    }

@shared_task
def parser_clarion():
    # return 'Success'
    site = get_site()
    soup = get_soup(site)
    menu = soup.find('ul', class_='art-hmenu')
    categories = menu.findChildren(recursive=False)
    get_categories(categories)
    return 'Парсинг категории завершен'


if __name__ == '__main__':
    parser_clarion()
