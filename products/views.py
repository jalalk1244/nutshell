from django.shortcuts import render

# Create your views here.
def products(request):
    '''View for the products page'''
    return render(request, 'products/products.html')