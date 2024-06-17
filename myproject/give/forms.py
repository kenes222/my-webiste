from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import *
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.mail import send_mail

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=254, required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(max_length=128, required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))



class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['username', 'avatar']

    def clean_username(self):
        username = self.cleaned_data['username']
        if Profile.objects.filter(username=username).exclude(user=self.instance.user).exists():
            raise ValidationError("This username is already in use. Please choose another one.")
        return username
    

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'description', 'image', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }


class SearchForm(forms.Form):
    query = forms.CharField(max_length=255, required=True)


class MessageForm(forms.ModelForm):
    class Meta:
        model = PrivateMessage
        fields = ['text', 'file']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 5}),
        }







