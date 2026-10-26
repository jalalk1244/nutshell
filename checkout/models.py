import uuid

from django.db import models

from django_countries.fields import CountryField

from products.models import Product
from profiles.models import UserProfile


class Order(models.Model):
    order_number = models.CharField(max_length=32, null=False, editable=False, unique=True)
    user_profile = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='orders')
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    country = CountryField(blank_label='Country *', null=False, blank=False)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    county = models.CharField(max_length=80, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    delivery_cost = models.DecimalField(
        max_digits=6, decimal_places=2, null=False, default=0
    )
    order_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, default=0
    )
    grand_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, default=0
    )
    original_bag = models.TextField(null=False, blank=False, default='')
    stripe_pid = models.CharField(
        max_length=254, null=False, blank=False, default=''
    )

    checkout_key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    payment_status = models.CharField(max_length=12, default='legacy', choices=[
        ('legacy', 'Unverified legacy order'), ('pending', 'Awaiting payment'),
        ('failed', 'Payment failed'), ('paid', 'Paid')])
    currency = models.CharField(max_length=3, default='usd')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['stripe_pid'],
            condition=~models.Q(stripe_pid=''), name='unique_nonempty_payment_intent')]

    def _generate_order_number(self):
        '''
        Generate a random, unique order number UUID
        '''
        return uuid.uuid4().hex.upper()

    def save(self, *args, **kwargs):
        '''
        Override the original save method to set the order number
        if it hasn't been set already
        '''
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderLineItem(models.Model):
    order = models.ForeignKey(
        Order, null=False, blank=False,
        on_delete=models.CASCADE, related_name='lineitems'
    )
    product = models.ForeignKey(
        Product, null=False, blank=False, on_delete=models.PROTECT
    )
    unit_price = models.DecimalField(max_digits=6, decimal_places=2, null=True, editable=False)
    quantity = models.IntegerField(null=False, blank=False, default=1)
    lineitem_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, blank=False, editable=False
    )

    class Meta:
        constraints = [models.CheckConstraint(condition=models.Q(quantity__gte=1, quantity__lte=99), name='order_quantity_1_to_99')]

    def save(self, *args, **kwargs):
        '''
        Override the original save method to set the lineitem total
        from the saved unit-price snapshot. Checkout calculates order totals
        explicitly in the same transaction as line-item creation.
        '''
        if self.unit_price is None:
            self.unit_price = self.product.price
        self.lineitem_total = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f'SKU {self.product.sku} on order {self.order.order_number}'


class PaymentEvent(models.Model):
    event_id = models.CharField(max_length=255, unique=True)
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    event_type = models.CharField(max_length=80)
    received_at = models.DateTimeField(auto_now_add=True)
