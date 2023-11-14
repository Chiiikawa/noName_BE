from django import forms

#이미지 사이즈 선택
class ProductSizeForm(forms.Form):
    size_choices = (
        ('A4', 'A4'),
        ('A5', 'A5'),
        ('B4', 'B4'),
    )
    productsize_choice_field = forms.ChoiceField(
        choices=size_choices, 
        widget=forms.Select(attrs={'class': 'form-control'})
        )
    
#이미지 프레임 선택
class ProductFrameForm(forms.Form):
    frame_choices = (
        ('Black', 'Black'),
        ('Wood', 'Wood'),
        ('White', 'White'),
    )
    productframe_choice_field = forms.ChoiceField(
        choices=frame_choices, 
        widget=forms.Select(attrs={'class': 'form-control'})
        )