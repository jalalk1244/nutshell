from django import template
from ..models import ProductRating


register = template.Library()


@register.filter(name='calc_stars')
def calc_stars(rating):
    return range(rating)
