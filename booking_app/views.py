from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Booking
from .forms import BookingForm, RoomForm, BookingAdminForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

@login_required
def room_list(request):
    rooms = Room.objects.filter(status='available')
    capacity = request.GET.get('capacity')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    
    filters = {'status': 'available'}
    if capacity:
        filters['capacity__gte'] = capacity
    if price_min:
        filters['price_per_night__gte'] = price_min
    if price_max:
        filters['price_per_night__lte'] = price_max

    rooms = Room.objects.filter(**filters)
    
    return render(request, 'booking_app/room_list.html', {'rooms': rooms})

@login_required
def book_room(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)

            # Комната уже объект Room
            room = form.cleaned_data.get('room')
            booking.room = room
            booking.guest = request.user
            booking.save()

            send_mail(
                'Подтверждение бронирования',
                f'Ваше бронирование {booking.room.title} подтверждено!',
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
            )

            messages.success(request, f'Бронь на {booking.room.title} успешно создана!')
            return redirect('booking_app:booking_list')
    else:
        form = BookingForm()

    return render(request, 'booking_app/book_room.html', {'form': form})

@login_required
def room_add_view(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('booking_app:room_manage')
    else:
        form = RoomForm()
    return render(request, 'booking_app/room_form.html', {'form': form, 'title': 'Добавить комнату'})

# UPDATE
@login_required
def room_edit_view(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('booking_app:room_manage')
    else:
        form = RoomForm(instance=room)
    return render(request, 'booking_app/room_form.html', {'form': form, 'title': 'Редактировать комнату'})

@login_required
def room_delete_view(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        room.delete()
    return redirect('booking_app:room_manage')

@login_required
def room_manage_view(request):
    rooms = Room.objects.all() 
    return render(request, 'booking_app/room_manage.html', {'rooms': rooms})

@login_required
def booking_list_view(request):
    """Список всех бронирований для админа"""
    bookings = Booking.objects.all().order_by('-check_in')
    return render(request, 'booking_app/booking_list.html', {'bookings': bookings})


@login_required
def booking_add_view(request, room_id=None):
    """Создание брони (админ может выбрать любого гостя)"""
    if room_id:
        room = get_object_or_404(Room, id=room_id)
    else:
        room = None

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            if room:
                booking.room = room
            booking.save()
            # Отправка email уведомления гостю
            send_mail(
                'Подтверждение бронирования',
                f'Ваше бронирование {booking.room.title} подтверждено!',
                settings.DEFAULT_FROM_EMAIL,
                [booking.guest.email],
            )
            messages.success(request, "Бронь успешно создана!")
            return redirect('booking_app:booking_list')
    else:
        form = BookingForm(initial={'room': room} if room else {})

    return render(request, 'booking_app/booking_form.html', {'form': form, 'room': room, 'title': 'Создать бронь'})


@login_required
def booking_edit_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    if request.method == 'POST':
        form = BookingAdminForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, "Бронь успешно обновлена!")
            return redirect('booking_app:booking_manage')
    else:
        form = BookingAdminForm(instance=booking)

    return render(request, 'booking_app/booking_edit.html', {
        'form': form,
        'title': 'Редактировать бронь (админ)'
    })

@login_required
def booking_confirm_view(request, pk):
    """Подтверждение брони (админ)"""
    booking = get_object_or_404(Booking, pk=pk)
    if booking.status != 'confirmed':
        booking.status = 'confirmed'
        booking.save()
        messages.success(request, "Бронь подтверждена!")
        # Отправка email гостю
        send_mail(
            'Бронь подтверждена',
            f'Ваше бронирование {booking.room.title} подтверждено!',
            settings.DEFAULT_FROM_EMAIL,
            [booking.guest.email],
        )
    return redirect('booking_app:booking_list')

@login_required
def booking_manage_view(request):
    """Страница управления всеми бронями (для админа)"""
    bookings = Booking.objects.all().order_by('-check_in')
    return render(request, 'booking_app/booking_manage.html', {'bookings': bookings})
