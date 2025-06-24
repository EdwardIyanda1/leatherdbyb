from django import forms
from .models import Address, UserProfile

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            'type', 'name', 'phone', 
            'line1', 'line2', 'city', 
            'state', 'postal_code', 'is_default'
        ]
        widgets = {
            'type': forms.Select(attrs={'class': 'form-input'}),
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'line1': forms.TextInput(attrs={'class': 'form-input'}),
            'line2': forms.TextInput(attrs={'class': 'form-input'}),
            'city': forms.TextInput(attrs={'class': 'form-input'}),
            'state': forms.Select(attrs={'class': 'form-input'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-input'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'date_of_birth', 'gender', 'profile_image']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-input'}),
        }