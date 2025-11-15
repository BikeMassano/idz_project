from django import forms
from .models import User
from booking_app.models import Room

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['title', 'description', 'capacity', 'price_per_night', 'status']