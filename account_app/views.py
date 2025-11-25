from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from .forms import UserRegistrationForm, UserUpdateForm
from django.contrib.auth.decorators import login_required
from booking_app.models import Room
from django.core.mail import send_mail
from django.conf import settings

# регистрация
def signup_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # отправка письма пользователю
            send_mail(
                subject='Добро пожаловать!',
                message=f'Здравствуйте, {user.username}! Вы успешно зарегистрировались.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,  # чтобы не упасть, если email не настроен
            )

            return redirect('account_app:login')
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
    
@login_required
def profile_edit_view(request):
    user = request.user

    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('account_app:profile')
    else:
        form = UserUpdateForm(instance=user)

    return render(request, 'registration/profile_edit.html', {'form': form})