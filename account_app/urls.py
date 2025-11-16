from django.urls import path
from .views import signup_view, CustomLoginView, profile_view
from django.contrib.auth.views import LogoutView
app_name = 'account_app'
urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/accounts/login/'), name='logout'),
    path('profile/', profile_view, name='profile'),
]