from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Администратор'),
        ('guest', 'Гость'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='guest')
    is_approved = models.BooleanField(default=False)
    objects = UserManager()

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"