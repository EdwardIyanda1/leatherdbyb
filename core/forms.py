from django import forms
from .models import Address, UserProfile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-input'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            'type', 'name', 'phone', 
            'line1', 'line2', 'city', 
            'state', 'postal_code', 'is_default'
        ]
        widgets = {
            'type': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'line1': forms.TextInput(attrs={'class': 'form-input'}),
            'line2': forms.TextInput(attrs={'class': 'form-input'}),
            'city': forms.TextInput(attrs={'class': 'form-input'}),
            'state': forms.Select(attrs={'class': 'form-select'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-input'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-checkbox'})
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