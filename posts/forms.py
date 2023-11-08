from django import forms

class ProductSizeForm(forms.Form):
    CHOICES = (
        ('A4', 'A4'),
        ('A5', 'A5'),
        ('B4', 'B4'),
    )
    choice_field = forms.ChoiceField(choices=CHOICES)