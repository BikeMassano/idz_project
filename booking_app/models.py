from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import date

User = settings.AUTH_USER_MODEL

class Room(models.Model):
    STATUS_CHOICES = (
        ('available', 'Доступен'),
        ('occupied', 'Занят'),
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    capacity = models.PositiveIntegerField()
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    objects = models.Manager()

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class Booking(models.Model):
    STATUS_CHOICES = (
        ('confirmed', 'Подтверждено'),
        ('cancelled', 'Отменено'),
    )
    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    guests_count = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='confirmed')
    objects = models.Manager()

    def clean(self):
        # Дата выезда > заезда
        if self.check_out <= self.check_in:
            raise ValidationError("Дата выезда должна быть позже даты заезда.")
        
        # Кол-во гостей <= вместимость
        if self.guests_count is not None and self.room.capacity is not None:
            if self.guests_count > self.room.capacity:
                raise ValidationError("Слишком много гостей для выбранной комнаты")

        # Дата заезда ≥ сегодня
        if self.check_in < date.today():
            raise ValidationError("Дата заезда не может быть в прошлом.")

        # Проверка перекрытия с другими бронями
        overlapping = Booking.objects.filter(
            room=self.room,
            check_out__gt=self.check_in,
            check_in__lt=self.check_out
        ).exclude(pk=self.pk)
        if overlapping.exists():
            raise ValidationError("Комната уже забронирована на эти даты.")

    def __str__(self):
        return f"Бронь #{self.id} — {self.room.title} для {self.guest.username}"


class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    objects = models.Manager()

    def __str__(self):
        return self.name


class ServiceOrder(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='service_orders')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def __str__(self):
        return f"{self.service.name} ×{self.quantity} (бронь #{self.booking.id})"
    
class Review(models.Model):
    booking = models.OneToOneField('Booking', on_delete=models.CASCADE, related_name='review')
    guest = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Отзыв к брони #{self.booking.id} — {self.comment}"
    

def update_room_status(room):
    """Обновляем статус комнаты в зависимости от активных броней."""
    active_booking = room.booking_set.filter(
        status='confirmed',
        check_in__lte=date.today(),
        check_out__gt=date.today()
    ).exists()
    room.status = 'occupied' if active_booking else 'available'
    room.save()