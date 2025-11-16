from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Booking, ServiceOrder, Service, Review, update_room_status
from .forms import BookingForm, RoomForm, BookingAdminForm, ServiceOrderForm, ServiceForm, ReviewForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from datetime import date
from django.core.exceptions import PermissionDenied

def admin_required(view_func):
    """
    Декоратор для проверки, что пользователь — админ.
    Если нет — выбрасывает PermissionDenied.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not (request.user.role == 'admin' or request.user.is_superuser):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)  
    return wrapper

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
def book_room(request, room_id=None):
    room = get_object_or_404(Room, id=room_id) if room_id else None

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.room = form.cleaned_data.get('room') or room
            booking.guest = request.user
            booking.save()

            update_room_status(booking.room)

            send_mail(
                subject='Бронь подтверждена',
                message=f'Здравствуйте, {request.user.username}!\n'
                        f'Ваше бронирование {booking.room.title} с {booking.check_in} по {booking.check_out} подтверждено.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=True,
            )

            messages.success(request, f'Бронь на {booking.room.title} успешно создана!')
            return redirect('account_app:profile')
    else:
        # Передаём room в initial, чтобы поле было заполнено
        form = BookingForm(initial={'room': room} if room else {})

    return render(request, 'booking_app/book_room.html', {'form': form, 'room': room})

@login_required
@admin_required
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
@admin_required
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
@admin_required
def room_delete_view(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        room.delete()
    return redirect('booking_app:room_manage')

@login_required
@admin_required
def room_manage_view(request):
    rooms = Room.objects.all() 
    return render(request, 'booking_app/room_manage.html', {'rooms': rooms})

@login_required
@admin_required
def booking_list_view(request):
    """Список всех бронирований для админа"""
    bookings = Booking.objects.all().order_by('-check_in')
    return render(request, 'booking_app/booking_list.html', {'bookings': bookings})


@login_required
@admin_required
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
                fail_silently=True,
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
@admin_required
def booking_confirm_view(request, pk):
    """Подтверждение брони (админ)"""
    booking = get_object_or_404(Booking, pk=pk)
    if booking.status != 'confirmed':
        booking.status = 'confirmed'
        update_room_status(booking.room)
        booking.save()
        messages.success(request, "Бронь подтверждена!")
        send_mail(
            'Бронь подтверждена',
            f'Ваше бронирование {booking.room.title} подтверждено!',
            settings.DEFAULT_FROM_EMAIL,
            [booking.guest.email],
            fail_silently=True,
        )
    return redirect('booking_app:booking_manage')

@login_required
@admin_required
def booking_manage_view(request):
    """Страница управления всеми бронями (для админа)"""
    bookings = Booking.objects.all().order_by('-check_in')
    return render(request, 'booking_app/booking_manage.html', {'bookings': bookings})


@login_required
def booking_cancel_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    # Проверяем, чья это бронь
    is_user = booking.guest == request.user

    if booking.status == 'confirmed':
        booking.status = 'cancelled'
        booking.save()
        update_room_status(booking.room)
        if booking.guest.email:
            send_mail(
                'Бронь отменена',
                f'Ваше бронирование {booking.room.title} с {booking.check_in} по {booking.check_out} было отменено.',
                settings.DEFAULT_FROM_EMAIL,
                [booking.guest.email],
                fail_silently=True,
            )

        messages.success(request, f"Бронь #{booking.id} успешно отменена!")

    # Если пользователь отменил свою бронь → в профиль
    if is_user:
        return redirect('account_app:profile')

    # Если админ → в админку
    return redirect('booking_app:booking_manage')


@login_required
def booking_delete_view(request, pk):
    """Удаление брони"""
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        booking.delete()
        room = booking.room
        update_room_status(room)
        messages.success(request, f"Бронь #{booking.id} успешно удалена!")
    return redirect('booking_app:booking_manage')

@login_required
def user_booking_services(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, guest=request.user)
    services = booking.service_orders.all()

    if request.method == 'POST':
        # Обработка добавления новой услуги
        if 'add_service' in request.POST:
            form = ServiceOrderForm(request.POST)
            if form.is_valid():
                service_order = form.save(commit=False)
                service_order.booking = booking
                service_order.save()
                # email уведомление
                send_mail(
                    subject='Услуга добавлена к бронированию',
                    message=f'Вы добавили услугу {service_order.service.name} '
                            f'к бронированию #{booking.id}.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[request.user.email],
                    fail_silently=True,
                )
                messages.success(request, "Услуга успешно добавлена!")
                return redirect('booking_app:user_booking_services', booking_id=booking.id)
        # Обработка удаления услуги
        elif 'delete_service' in request.POST:
            service_id = request.POST.get('service_id')
            service_order = get_object_or_404(ServiceOrder, id=service_id, booking=booking)
            service_order.delete()
            # email уведомление
            send_mail(
                subject='Услуга удалена из бронирования',
                message=f'Вы удалили услугу {service_order.service.name} '
                        f'из бронирования #{booking.id}.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=True,
            )
            messages.success(request, "Услуга удалена!")
            return redirect('booking_app:user_booking_services', booking_id=booking.id)
        # Обработка изменения услуги
        elif 'update_service' in request.POST:
            service_id = request.POST.get('service_id')
            service_order = get_object_or_404(ServiceOrder, id=service_id, booking=booking)
            form = ServiceOrderForm(request.POST, instance=service_order)
            if form.is_valid():
                form.save()
                # email уведомление
                send_mail(
                    subject='Услуга обновлена в бронировании',
                    message=f'Вы обновили услугу {service_order.service.name} '
                            f'в бронировании #{booking.id}.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[request.user.email],
                    fail_silently=True,
                )
                messages.success(request, "Услуга обновлена!")
                return redirect('booking_app:user_booking_services', booking_id=booking.id)
    else:
        form = ServiceOrderForm()

    return render(request, 'booking_app/user_services.html', {
        'booking': booking,
        'services': services,
        'form': form
    })

@login_required
def update_user_service(request, service_id):
    service_order = get_object_or_404(ServiceOrder, id=service_id, booking__guest=request.user)

    if request.method == 'POST':
        form = ServiceOrderForm(request.POST, instance=service_order)
        if form.is_valid():
            form.save()

            send_mail(
                'Обновление услуги',
                f'Вы изменили услуги для бронирования {service_order.booking.id}.',
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                fail_silently=True,
            )
            messages.success(request, "Услуга обновлена!")
            return redirect('booking_app:user_booking_services', booking_id=service_order.booking.id)
    else:
        form = ServiceOrderForm(instance=service_order)

    return render(request, 'booking_app/update_service.html', {'form': form, 'service_order': service_order})

@login_required
@admin_required
def service_manage_view(request):
    services = Service.objects.all()
    return render(request, 'booking_app/service_manage.html', {'services': services})

# Добавление услуги
@login_required
@admin_required
def service_add_view(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Услуга успешно добавлена!")
            return redirect('booking_app:service_manage')
    else:
        form = ServiceForm()
    return render(request, 'booking_app/service_form.html', {'form': form, 'title': 'Добавить услугу'})

# Редактирование услуги
@login_required
@admin_required
def service_edit_view(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, "Услуга успешно обновлена!")
            return redirect('booking_app:service_manage')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'booking_app/service_form.html', {'form': form, 'title': 'Редактировать услугу'})

# Удаление услуги
@login_required
@admin_required
def service_delete_view(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.delete()
        messages.success(request, "Услуга успешно удалена!")
    return redirect('booking_app:service_manage')

@login_required
def add_review(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, guest=request.user)
    
    if hasattr(booking, 'review'):
        return redirect('booking_app:edit_review', booking_id=booking.id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.guest = request.user 
            review.save()
            return redirect('account_app:profile')
    else:
        form = ReviewForm()
    
    return render(request, 'booking_app/review_form.html', {'form': form, 'booking': booking})

@login_required
def edit_review(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, guest=request.user)
    review = get_object_or_404(Review, booking=booking)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('account_app:profile')
    else:
        form = ReviewForm(instance=review)
    
    return render(request, 'booking_app/review_form.html', {'form': form, 'booking': booking})