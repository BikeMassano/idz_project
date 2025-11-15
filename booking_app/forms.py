from django import forms
from .models import Booking, ServiceOrder, Room
from django.contrib.auth import get_user_model
from account_app.models import User

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['room', 'check_in', 'check_out', 'guests_count']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date'}),
            'check_out': forms.DateInput(attrs={'type': 'date'}),
        }

class ServiceOrderForm(forms.ModelForm):
    class Meta:
        model = ServiceOrder
        fields = ['service', 'quantity']

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class FeedbackForm(forms.Form):
    subject = forms.CharField(max_length=255)
    message = forms.CharField(widget=forms.Textarea)

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['title', 'description', 'capacity', 'price_per_night', 'status']

class BookingAdminForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['room', 'check_in', 'check_out', 'guests_count', 'status']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date'}),
            'check_out': forms.DateInput(attrs={'type': 'date'}),
        }