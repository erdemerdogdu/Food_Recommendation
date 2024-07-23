from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['meal', 'comment', 'service_rating', 'taste_rating', 'delivery_rating']
        widgets = {
            'meal': forms.HiddenInput(),
            'comment': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your comment'}),
            'service_rating': forms.NumberInput(attrs={'class': 'notseen', 'placeholder': 'Service Rating', 'style': 'display:none;'}),
            'taste_rating': forms.NumberInput(attrs={'class': 'notseen', 'placeholder': 'Taste Rating', 'style': 'display:none;'}),
            'delivery_rating': forms.NumberInput(attrs={'class': 'notseen', 'placeholder': 'Delivery Rating', 'style': 'display:none;'}),
        }
