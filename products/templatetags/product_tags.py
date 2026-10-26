from django import template
from ..models import ProductRating
from bag.views import get_cart_info
from django.templatetags.static import static


register = template.Library()

# Only these identified legacy stock files are replaced. Custom uploads retain
# their configured media-storage URL; no database or storage migration is needed.
LEGACY_CATALOGUE_IMAGES = {
    'dry_fruits.jpg': 'media/catalogue/dried-fruit-mix.webp',
    'seeds.jpg': 'media/catalogue/seed-mix.webp',
    'seeds_EO8exKU.jpg': 'media/catalogue/seed-mix.webp',
}


@register.filter
def product_image_url(product):
    image = product.image
    if not image:
        return ''
    replacement = LEGACY_CATALOGUE_IMAGES.get(image.name)
    return static(replacement) if replacement else image.url


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
