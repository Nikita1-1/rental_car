from django import forms
from django.contrib.auth.forms import UserCreationForm

from user_auths.models import User, Profile
from django.contrib.auth import get_user_model


User = get_user_model()

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email'
            }),
        }
class ProfileUpdateForm(forms.ModelForm):
    
    class Meta:
        model = Profile
        fields = [
            'full_name', 
            'phone',
            'image',
            'drivers_license',
            ]