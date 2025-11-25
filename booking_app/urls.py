from django.urls import path
from .views import add_review, booking_delete_view, booking_confirm_view, booking_edit_view, booking_list_view, booking_manage_view, booking_cancel_view, edit_review, room_add_view, room_edit_view, room_delete_view, book_room, room_list, room_manage_view, service_add_view, service_delete_view, service_edit_view, service_manage_view, update_user_service, user_booking_services
app_name = 'booking_app'
urlpatterns = [
    path('rooms/', room_list, name='room_list'),
    path('rooms/<int:room_id>/book/', book_room, name='book_room'),
    path('rooms/add/', room_add_view, name='room_add'),
    path('rooms/<int:pk>/edit/', room_edit_view, name='room_edit'),
    path('rooms/<int:pk>/delete/', room_delete_view, name='room_delete'),
    path('rooms/manage/', room_manage_view, name='room_manage'),
    path('bookings/', booking_list_view, name='booking_list'),
    path('booking/book/', book_room, name='book_room'),
    path('booking/<int:pk>/edit/', booking_edit_view, name='booking_edit'),
    path('booking/<int:pk>/confirm/', booking_confirm_view, name='booking_confirm'),
    path('bookings/manage/', booking_manage_view, name='booking_manage'),
    path('booking/<int:pk>/cancel/', booking_cancel_view, name='booking_cancel'),
    path('booking/<int:pk>/delete/', booking_delete_view, name='booking_delete'),
    path('booking/<int:booking_id>/services/', user_booking_services, name='user_booking_services'),
    path('service/<int:service_id>/update/', update_user_service, name='update_user_service'),
    path('services/manage/', service_manage_view, name='service_manage'),
    path('services/add/', service_add_view, name='service_add'),
    path('services/<int:pk>/edit/', service_edit_view, name='service_edit'),
    path('services/<int:pk>/delete/', service_delete_view, name='service_delete'),
    path('booking/<int:booking_id>/review/add/', add_review, name='add_review'),
    path('booking/<int:booking_id>/review/edit/', edit_review, name='edit_review'),
]