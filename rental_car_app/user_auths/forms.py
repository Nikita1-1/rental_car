from fileinput import FileInput
import re
from django import forms
from django.contrib.auth.forms import UserCreationForm

from user_auths.models import User, Profile

class UserRegisterForm(UserCreationForm):
    full_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':"Enter Full Name"}))
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder':"Enter Username"}))
    email = forms.CharField(widget=forms.TextInput(attrs={'placeholder':"Enter Email"}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder':"Enter Phone"}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':"Enter Password"}))
    
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':"Confirm Password"}))
    
    drivers_license = forms.FileField(required=True)

    class Meta:
        model = User
        fields = ['full_name', 'username', 'email', 'phone', 'password1', 'password2', 'drivers_license']

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password:
            if len(password) < 8:
                raise forms.ValidationError("Password must be at least 8 characters long.")
            if not re.search(r'[A-Z]', password):
                raise forms.ValidationError('Password must contain at least one uppercase letter.')
            if not re.search(r'[a-z]', password):
                raise forms.ValidationError('Password must contain at least one lowercase letter.')
            if not re.search(r'[!@#$%^&*()_+~{}:"<>?,./;]', password):
                raise forms.ValidationError('Password must contain at least one special character.')
        return password

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email',]

class ProfileUpdateForm(forms.ModelForm):
    
    class Meta:
        model = Profile
        fields = [
            'full_name', 
            'phone',
            'image',
            'drivers_license',
            ]

        

# class ProfileUpdateForm(forms.ModelForm):
    
#     class Meta:
#         model = Profile
#         fields = [
#             'image',
#             'full_name', 
#             'phone',
#             'drivers_license'
#         ]