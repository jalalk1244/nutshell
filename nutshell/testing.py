from products.models import Product

def make_product(**kwargs):
    data = dict(name='Walnuts', slug='walnuts', price='4.99', description='Fresh walnuts')
    data.update(kwargs)
    product = Product.objects.create(**data)
    product.refresh_from_db()
    return product

def address(**kwargs):
    data = dict(full_name='Test Customer', email='test@example.invalid', phone_number='123456',
                country='SE', postcode='10000', town_or_city='Stockholm',
                street_address1='Test street 1', street_address2='', county='')
    data.update(kwargs)
    return data
