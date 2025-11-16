from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from booking_app.models import Room, Booking, Service, ServiceOrder
from datetime import date, timedelta

User = get_user_model()

class BookingAppTests(TestCase):
    # подготовка
    def setUp(self):
        # Создание пользователя
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass', 
            email='test@example.com')
        
        self.client = Client()
        self.client.login(username='testuser', password='testpass')

        # Создание комнаты
        self.room = Room.objects.create(
            title='Room 101',
            capacity=2,
            price_per_night=100,
            status='available'
        )

        # Создание услуги
        self.service = Service.objects.create(
            name='Breakfast',
            price=20
        )

        # Создание брони
        self.booking = Booking.objects.create(
            room=self.room,
            guest=self.user,
            guests_count=1,
            check_in=date.today(),
            check_out=date.today() + timedelta(days=2),
            status='pending'
        )

    def test_room_list_view(self):
        """Проверка фильтрации комнат"""
        response = self.client.get(reverse('booking_app:room_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Room 101')

    def test_room_list_with_filters(self):
        """Проверка фильтрации по capacity и цене"""
        response = self.client.get(reverse('booking_app:room_list') + '?capacity=1&price_min=50&price_max=150')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Room 101')

    def test_book_room_view(self):
        self.client.force_login(self.user)
        """Создание брони пользователем"""
        response = self.client.post(reverse('booking_app:book_room'), {
            'room': self.room.id,
            'check_in': (date.today() + timedelta(days=3)).strftime('%Y-%m-%d'),
            'check_out': (date.today() + timedelta(days=4)).strftime('%Y-%m-%d'),
            'guests_count': 2,
        })
        self.assertEqual(response.status_code, 302)  # Redirect после успешной брони
        self.assertTrue(Booking.objects.filter(guest=self.user, room=self.room).exists())

    def test_booking_cancel_view(self):
        """Отмена брони пользователем"""
        self.booking.status = 'confirmed'
        self.booking.save()
        response = self.client.get(reverse('booking_app:booking_cancel', args=[self.booking.id]))
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'cancelled')

    def test_add_service_to_booking(self):
        """Добавление услуги к бронированию"""
        response = self.client.post(reverse('booking_app:user_booking_services', args=[self.booking.id]), {
            'add_service': True,
            'service': self.service.id,
            'quantity': 1
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ServiceOrder.objects.filter(booking=self.booking, service=self.service).exists())

    def test_update_service_order(self):
        """Обновление услуги"""
        service_order = ServiceOrder.objects.create(booking=self.booking, service=self.service, quantity=1)
        response = self.client.post(reverse('booking_app:update_user_service', args=[service_order.id]), {
            'service': self.service.id,
            'quantity': 3
        })
        service_order.refresh_from_db()
        self.assertEqual(service_order.quantity, 3)

    def test_service_add_edit_delete(self):
        """CRUD для услуги"""
        # Добавление
        response = self.client.post(reverse('booking_app:service_add'), {'name': 'Spa', 'price': 50})
        self.assertTrue(Service.objects.filter(name='Spa').exists())

        service = Service.objects.get(name='Spa')

        # Редактирование
        response = self.client.post(reverse('booking_app:service_edit', args=[service.id]), {'name': 'Spa Deluxe', 'price': 60})
        service.refresh_from_db()
        self.assertEqual(service.name, 'Spa Deluxe')

        # Удаление
        response = self.client.post(reverse('booking_app:service_delete', args=[service.id]))
        self.assertFalse(Service.objects.filter(id=service.id).exists())

    def test_room_add_edit_delete(self):
        """CRUD для комнаты"""
        # Добавление
        response = self.client.post(reverse('booking_app:room_add'), {
            'title': 'Room 102',
            'description': 'Test description',
            'capacity': 3,
            'price_per_night': 120,
            'status': 'available'
        })
        self.assertTrue(Room.objects.filter(title='Room 102').exists())
        room = Room.objects.get(title='Room 102')

        # Редактирование
        response = self.client.post(reverse('booking_app:room_edit', args=[room.id]), {
            'title': 'Room 102 Updated', 
            'description': 'Updated description',
            'capacity': 3, 
            'price_per_night': 130, 
            'status': 'available'
            })
        room.refresh_from_db()
        self.assertEqual(room.title, 'Room 102 Updated')
        self.assertEqual(room.price_per_night, 130)

        # Удаление
        response = self.client.post(reverse('booking_app:room_delete', args=[room.id]))
        self.assertFalse(Room.objects.filter(id=room.id).exists())
