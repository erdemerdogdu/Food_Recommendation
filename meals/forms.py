from django import forms
from .models import  Meal


class MealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ['name', 'description', 'price', 'cuisine_type', 'restaurant']
        widgets = {
            'restaurant': forms.HiddenInput(),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price'}),
            'cuisine_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'cuisine_type'}),
        }
