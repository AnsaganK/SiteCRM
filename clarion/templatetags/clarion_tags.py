from django import template

register = template.Library()

def category_tree(category, zero=1):
    zero += 1
    categories_list = []
    if category.children:
        category_children = category.children.all()
        for category_child in category_children:
            tree = category_tree(category_child, zero)
            categories_list.append({'category': category_child, 'children': tree})
        return categories_list
    else:
        return category


@register.filter(name='show_categories')
def show_categories(categories):
    categories_list = []
    for category in categories:
        if category.children:
            tree = category_tree(category)
            categories_list.append({'category': category, 'children': tree})
    return categories_list


@register.filter(name='show_rating')
def show_rating(rating):
    full_star_count = '<i class="fa fa-star"></i>'*int(rating)
    empty_star_count = '<i class="fa fa-star-o"></i>'*(5-int(rating))
    return full_star_count+empty_star_count


@register.filter(name='isWriteReview')
def isWriteReview(user, page):
    if user.reviews.filter(page=page).first():
        return True
    return False