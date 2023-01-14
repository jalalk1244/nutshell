from django.db import models
from django.contrib.auth.models import User

# Create your models here.
STARS = (
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
)


class Category(models.Model):

    class Meta:
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=200)
    slug = models.SlugField(null=False, unique=True)

    def __str__(self):
        return self.name


class Subcategory(models.Model):

    class Meta:
        verbose_name_plural = 'Subcategories'

    name = models.CharField(max_length=200)
    slug = models.SlugField(null=False, unique=True)
    parent_category = models.ForeignKey('Category', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=254, null=True, blank=True)
    slug = models.SlugField(null=False, unique=True)
    image = models.ImageField(null=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.ForeignKey('Category', null=True, blank=True, on_delete=models.SET_NULL)
    sub_category = models.ForeignKey('Subcategory', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class ProductRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    title = models.CharField(max_length=60, null=False, blank=False)
    rating = models.IntegerField(choices=STARS)
    comment = models.TextField(null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_review_rating(self):
        return self.review_rating


class WishList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wished_product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.wished_product.name
