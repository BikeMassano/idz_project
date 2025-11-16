from django.urls import path
from . import views
from .views import booking_delete_view, booking_confirm_view, booking_edit_view, booking_list_view, booking_manage_view, booking_cancel_view, room_add_view, room_edit_view, room_delete_view, book_room, room_list, room_manage_view
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
    path('booking/<int:booking_id>/services/', views.user_booking_services, name='user_booking_services'),
    path('service/<int:service_id>/update/', views.update_user_service, name='update_user_service'),
    path('services/manage/', views.service_manage_view, name='service_manage'),
    path('services/add/', views.service_add_view, name='service_add'),
    path('services/<int:pk>/edit/', views.service_edit_view, name='service_edit'),
    path('services/<int:pk>/delete/', views.service_delete_view, name='service_delete'),
    path('booking/<int:booking_id>/review/add/', views.add_review, name='add_review'),
    path('booking/<int:booking_id>/review/edit/', views.edit_review, name='edit_review'),
]