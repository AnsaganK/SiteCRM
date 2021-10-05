import requests
from bs4 import BeautifulSoup as BS

url = 'https://clarionherald.info/'
url2 = 'https://clarionherald.info/clarion/index.php/news'


def get_site(url=url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.text
    return None


def get_soup(response_text):
    html = BS(response_text, 'lxml')
    return html


def get_categories(categories, zero=0):
    zero += 1
    for category in categories:
        category_link = category.find('a')
        link = category_link['href']
        full_link = url+link
        print(detail_page(full_link))
        text = category_link.text
        print('    '*zero, link, ' : ', text)
        try:
            ul = category.find('ul')
            ul_categories = ul.findChildren(recursive=False)
            get_categories(ul_categories, zero)
        except:
            pass


def detail_page(page_url):
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


def parser_menu():
    site = get_site()
    soup = get_soup(site)
    menu = soup.find('ul', class_='art-hmenu')
    categories = menu.findChildren(recursive=False)
    get_categories(categories)



if __name__ == '__main__':
    parser_menu()