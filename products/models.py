from django.db import models

# Create your models here.


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
