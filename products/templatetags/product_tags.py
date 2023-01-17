from django import template
from ..models import ProductRating
from bag.views import get_cart_info


register = template.Library()


@register.filter(name='calc_stars')
def calc_stars(rating):
    return range(rating)


@register.simple_tag()
def number_of_cart_items(request):
    num_of_items = get_cart_info(request)['product_count']

    if num_of_items == 0:
        return ''
    else:
        return num_of_items
