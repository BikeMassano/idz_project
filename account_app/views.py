from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required
from booking_app.models import Room

# регистрация
def signup_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/signup.html', {'form': form})

# вход
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

@login_required
def profile_view(request):
    user = request.user
    if user.is_superuser:
        rooms = Room.objects.all()
        return render(request, 'registration/profile_admin.html', {
            'user': user,
            'rooms': rooms
        })
    elif user.role == 'admin':
        rooms = Room.objects.all()
        return render(request, 'registration/profile_admin.html', {
            'user': user,
            'rooms': rooms
        })
    else:
        return render(request, 'registration/profile.html', {'user': user})