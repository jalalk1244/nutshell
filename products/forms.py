from django import forms
from .models import ProductRating


class ReviewForm(forms.ModelForm):

    class Meta:
        model = ProductRating
        fields = ('title', 'rating', 'comment',)
