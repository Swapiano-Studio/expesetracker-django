from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    """Form for creating a new user with custom fields"""
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'job', 'income', 'country', 'city', 'address')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'job': forms.Select(attrs={'class': 'form-select'}),
            'income': forms.Select(attrs={'class': 'form-select'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to password fields
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        
        # Make some fields optional
        self.fields['job'].required = False
        self.fields['income'].required = False
        self.fields['country'].required = False
        self.fields['city'].required = False
        self.fields['address'].required = False
        
        # Add help texts
        self.fields['email'].help_text = 'Required. Enter a valid email address.'
        self.fields['job'].help_text = 'Optional. Select your current occupation.'
        self.fields['income'].help_text = 'Optional. Select your income range.'
