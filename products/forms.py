from django import forms
from .models import ProductRating, Product, Category, Subcategory


class ReviewForm(forms.ModelForm):

    class Meta:
        model = ProductRating
        fields = ('title', 'rating', 'comment',)


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        subcategories = Subcategory.objects.all()
        category_names = [(c.id, c.name) for c in categories]
        subcategories_name = [(s.id, s.name) for s in subcategories]

        self.fields['category'].choices = category_names
        self.fields['sub_category'].choices = subcategories_name
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'
